import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views import View
from requests import RequestException

from graph.services import (
    execute_delete_software_mfa_method,
    execute_list_user_authentication_methods,
    execute_microsoft_authentication_method,
    execute_phone_authentication_method,
)

from .forms import (
    BugReportForm,
    DeleteAuthenticationMethodForm,
    LargeTextAreaForm,
    MfaResetLookupForm,
)
from .models import BugReport, BugReportAttachment, Endpoint

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class BaseView(View):
    require_login = True  # By default, require login for all views inheriting from BaseView
    base_template = "myview/base.html"


    def user_has_mfa_reset_access(self):
        required_endpoints = [
            {'method': 'GET', 'path': '/graph/v1.0/get-user/{user}'},
            {'method': 'GET', 'path': '/graph/v1.0/list/{user_id__or__user_principalname}/authentication-methods'},
            {'method': 'DELETE', 'path': '/graph/v1.0/users/{user_id__or__user_principalname}/microsoft-authentication-methods/{microsoft_authenticator_method_id}'},
            {'method': 'DELETE', 'path': '/graph/v1.0/users/{user_id__or__user_principalname}/phone-authentication-methods/{phone_authenticator_method_id}'},
            {'method': 'DELETE', 'path': '/graph/v1.0/users/{user_id__or__user_principalname}/software-authentication-methods/{software_oath_method_id}'},
            {'method': 'GET', 'path': '/active-directory/v1.0/query'}
        ]

        # Fetch user's ad groups and user endpoints
        user_ad_groups = self.request.user.ad_group_members.all()
        user_endpoints = Endpoint.objects.filter(ad_groups__in=user_ad_groups).prefetch_related('ad_groups').distinct()

        user_endpoint_set = {(endpoint.method.upper(), endpoint.path) for endpoint in user_endpoints}

        result = all((endpoint['method'], endpoint['path']) in user_endpoint_set for endpoint in required_endpoints)
        return result


    def dispatch(self, request, *args, **kwargs):
        # The login_required decorator takes care of checking authentication,
        # so you don't need to manually check if the user is authenticated here.
        return super().dispatch(request, *args, **kwargs)

    def _locate_git_root(self):
        """Return the git repository root and git directory, if located."""

        current_path = Path(__file__).resolve().parent
        for path in (current_path,) + tuple(current_path.parents):
            git_entry = path / ".git"
            if not git_entry.exists():
                continue

            if git_entry.is_dir():
                return path, git_entry

            # Worktree checkouts store a pointer file instead of a directory
            gitdir_prefix = "gitdir:"
            gitdir_path = git_entry.read_text(encoding="utf-8").strip()
            if gitdir_path.startswith(gitdir_prefix):
                gitdir_path = gitdir_path[len(gitdir_prefix):].strip()

            gitdir_candidate = Path(gitdir_path)
            if not gitdir_candidate.is_absolute():
                gitdir_candidate = (path / gitdir_candidate).resolve()

            if gitdir_candidate.exists():
                return path, gitdir_candidate

        return None, None

    def _environment_git_info(self):
        """Return git metadata exposed through environment variables."""

        branch = None
        commit = None
        last_updated_formatted = None

        branch = (
            os.environ.get("COOLIFY_GIT_BRANCH")
            or os.environ.get("GIT_BRANCH")
            or os.environ.get("BRANCH")
        )

        commit = (
            os.environ.get("COOLIFY_GIT_COMMIT")
            or os.environ.get("GIT_COMMIT")
            or os.environ.get("SOURCE_VERSION")
            or os.environ.get("COMMIT")
        )

        last_updated_raw = (
            os.environ.get("COOLIFY_LAST_UPDATED")
            or os.environ.get("COOLIFY_DEPLOYED_AT")
            or os.environ.get("LAST_DEPLOYED_AT")
            or os.environ.get("LAST_UPDATED")
        )

        if last_updated_raw:
            last_updated_dt = parse_datetime(last_updated_raw)
            if last_updated_dt is None:
                if last_updated_raw.isdigit():
                    last_updated_dt = datetime.fromtimestamp(
                        int(last_updated_raw), tz=ZoneInfo("UTC")
                    )
                else:
                    try:
                        last_updated_dt = datetime.fromisoformat(last_updated_raw)
                    except ValueError:
                        last_updated_dt = None

            if last_updated_dt is not None:
                if last_updated_dt.tzinfo is None:
                    last_updated_dt = last_updated_dt.replace(tzinfo=ZoneInfo("UTC"))
                last_updated_dt = last_updated_dt.astimezone(
                    ZoneInfo("Europe/Copenhagen")
                )
                last_updated_formatted = last_updated_dt.strftime('%H:%M %d-%m-%Y %Z')
            else:
                last_updated_formatted = last_updated_raw

        return branch, commit, last_updated_formatted

    def _fallback_git_info(self, git_dir):
        """Read git information directly from the .git directory."""

        branch = "unknown"
        commit = "unknown"
        last_updated_formatted = "unknown"

        head_path = git_dir / "HEAD"
        if not head_path.exists():
            return branch, commit, last_updated_formatted

        head_contents = head_path.read_text(encoding="utf-8").strip()
        if head_contents.startswith("ref:"):
            ref = head_contents.partition(" ")[2]
            branch = ref.rsplit("/", 1)[-1] or branch
            ref_path = git_dir / ref
        else:
            ref_path = head_path
            commit = head_contents

        if ref_path.exists():
            commit = ref_path.read_text(encoding="utf-8").strip() or commit
            last_updated_dt = datetime.fromtimestamp(ref_path.stat().st_mtime, tz=ZoneInfo("Europe/Copenhagen"))
            last_updated_formatted = last_updated_dt.strftime('%H:%M %d-%m-%Y %Z')

        return branch, commit, last_updated_formatted

    def get_git_info(self):
        branch = "unknown"
        commit = "unknown"
        last_updated_formatted = "unknown"
        last_updated_raw = None

        git_root, git_dir = self._locate_git_root()

        env_branch, env_commit, env_last_updated = self._environment_git_info()
        if env_branch:
            branch = env_branch
        if env_commit:
            commit = env_commit
        if env_last_updated:
            last_updated_formatted = env_last_updated

        try:
            if not git_root:
                raise FileNotFoundError("Unable to locate git repository root")

            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=git_root,
            ).decode('utf-8').strip()
            commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                cwd=git_root,
            ).decode('utf-8').strip()
            last_updated_raw = subprocess.check_output(
                ['git', 'log', '-1', '--format=%cd'],
                cwd=git_root,
            ).decode('utf-8').strip()

            # Parse the last_updated date string and reformat it
            last_updated_dt = datetime.strptime(last_updated_raw, '%a %b %d %H:%M:%S %Y %z')
            last_updated_dt = last_updated_dt.astimezone(ZoneInfo("Europe/Copenhagen"))
            last_updated_formatted = last_updated_dt.strftime('%H:%M %d-%m-%Y %Z')
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.warning("Unable to read git metadata for template footer: %s", exc)
            if git_dir:
                branch, commit, last_updated_formatted = self._fallback_git_info(git_dir)
            if last_updated_raw:
                last_updated_formatted = last_updated_raw
        except ValueError as exc:
            logger.warning("Unable to parse git commit timestamp '%s': %s", last_updated_raw, exc)
            if last_updated_raw:
                last_updated_formatted = last_updated_raw

        return branch, commit, last_updated_formatted

    def get_context_data(self, **kwargs):
        branch, commit, last_updated = self.get_git_info()
        
        # Existing context setup
        user_ad_groups = self.request.user.ad_group_members.all()
        user_endpoints = Endpoint.objects.filter(ad_groups__in=user_ad_groups).prefetch_related('ad_groups').distinct()
        user_ad_group_ids = user_ad_groups.values_list('id', flat=True)

        # Filter endpoints to include only user-specific group access information
        filtered_endpoints = []
        available_limiter_types = set()
        for endpoint in user_endpoints:
            filtered_groups = endpoint.ad_groups.filter(members=self.request.user)
            limiter_label = endpoint.limiter_type.name if endpoint.limiter_type else "None"
            available_limiter_types.add(limiter_label)
            filtered_endpoints.append({
                'id': endpoint.id,
                'method': endpoint.method,
                'path': endpoint.path,
                'ad_groups': filtered_groups,
                'limiter_type': limiter_label,
                'no_limit': endpoint.no_limit
            })

        # Fetch Limiter Types that the user is associated with
        from .models import LimiterType, IPLimiter, ADOrganizationalUnitLimiter
        associated_limiter_types = []

        for limiter_type in LimiterType.objects.all():
            content_type = limiter_type.content_type

            if content_type.model == 'iplimiter':
                limiters = IPLimiter.objects.filter(ad_groups__in=user_ad_group_ids).distinct()
            elif content_type.model == 'adorganizationalunitlimiter':
                limiters = ADOrganizationalUnitLimiter.objects.filter(ad_groups__in=user_ad_group_ids).distinct()
            else:
                limiters = []

            if limiters.exists():
                limiter_type_info = {
                    'name': limiter_type.name,
                    'description': limiter_type.description,
                    'model': content_type.model,
                    'canonical_names': ', '.join(limiters.values_list('canonical_name', flat=True).distinct()) if content_type.model == 'adorganizationalunitlimiter' else None,
                }
                associated_limiter_types.append(limiter_type_info)

        from django.conf import settings
        context = {
            'base_template': self.base_template,
            'git_branch': branch,
            'git_commit': commit,
            'last_updated': last_updated,
            'is_superuser': self.request.user.is_superuser,
            'user_endpoints': filtered_endpoints,
            'user_ad_groups': user_ad_groups,
            'user_has_mfa_reset_access': self.user_has_mfa_reset_access(),
            'debug': settings.DEBUG,
            'all_limiter_types': associated_limiter_types,
            'available_limiter_types': sorted(available_limiter_types),
            'bug_report_form': BugReportForm(),
        }

        return context


    def get(self, request, **kwargs):

        context = self.get_context_data(**kwargs)
        return render(request, self.base_template, context)


















































































@method_decorator(login_required, name='dispatch')
class FrontpagePageView(BaseView):
    template_name = "myview/frontpage.html"
    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        return render(request, self.template_name, context)



















































@method_decorator(login_required, name='dispatch')
class BugReportView(View):
    """Accept bug report submissions from the UI."""

    form_class = BugReportForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if not request.session.session_key:
            request.session.save()

        form = self.form_class(request.POST, request.FILES)

        if not form.is_valid():
            return JsonResponse(
                {"success": False, "errors": form.errors},
                status=400,
            )

        bug_report = form.save(commit=False)
        if request.user.is_authenticated:
            bug_report.user = request.user

        bug_report.session_key = request.session.session_key or ""
        cleaned_data = form.cleaned_data

        page_url = cleaned_data.get("page_url") or request.META.get("HTTP_REFERER") or ""
        bug_report.page_url = page_url[:2048]

        page_path = cleaned_data.get("page_path") or request.META.get("PATH_INFO") or request.path
        bug_report.page_path = page_path[:512]

        site_domain = cleaned_data.get("site_domain") or request.get_host() or ""
        bug_report.site_domain = site_domain[:255]

        bug_report.user_agent = request.META.get("HTTP_USER_AGENT", "")

        bug_report.save()

        attachments = cleaned_data.get("attachments") or []
        for uploaded_file in attachments:
            BugReportAttachment.objects.create(
                bug_report=bug_report,
                file=uploaded_file,
                original_name=getattr(uploaded_file, "name", ""),
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Thanks! Your bug report has been submitted to the team.",
                "bug_report_id": bug_report.pk,
            },
            status=201,
        )

class GraphAPIError(Exception):
    """Lightweight wrapper for surfacing Graph API errors to the UI."""


class MFAResetPageView(BaseView):
    template_name = "myview/mfa-reset.html"
    form_class = MfaResetLookupForm
    delete_form_class = DeleteAuthenticationMethodForm

    DELETE_HANDLERS = {
        "#microsoft.graph.microsoftAuthenticatorAuthenticationMethod": (
            "Microsoft Authenticator",
            execute_microsoft_authentication_method,
        ),
        "#microsoft.graph.phoneAuthenticationMethod": (
            "Phone",
            execute_phone_authentication_method,
        ),
        "#microsoft.graph.softwareOathAuthenticationMethod": (
            "Software OATH",
            execute_delete_software_mfa_method,
        ),
    }

    def get(self, request, *args, **kwargs):
        if not self.user_has_mfa_reset_access():
            return HttpResponseForbidden("You do not have access to this page.")

        context = super().get_context_data(**kwargs)
        user_principal_name = request.GET.get("userPrincipalName", "").strip()
        lookup_form = self.form_class(
            initial={"user_principal_name": user_principal_name}
        ) if user_principal_name else self.form_class()

        auth_methods = []
        no_methods = False

        if user_principal_name:
            try:
                data = self._fetch_authentication_methods(user_principal_name)
                auth_methods = self._transform_methods(data)
                no_methods = not auth_methods
            except GraphAPIError as exc:
                messages.error(request, str(exc))

        context.update(
            {
                "lookup_form": lookup_form,
                "authentication_methods": auth_methods,
                "selected_user_principal_name": user_principal_name,
                "no_methods": no_methods,
            }
        )
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not self.user_has_mfa_reset_access():
            return HttpResponseForbidden("You do not have access to this page.")

        action = request.POST.get("action", "lookup")
        if action == "delete":
            return self._handle_delete(request)
        return self._handle_lookup(request, **kwargs)

    def _handle_lookup(self, request, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user_principal_name = form.cleaned_data["user_principal_name"]
            query = urlencode({"userPrincipalName": user_principal_name})
            return redirect(f"{reverse('mfa-reset')}?{query}")

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "lookup_form": form,
                "authentication_methods": [],
                "selected_user_principal_name": "",
                "no_methods": False,
            }
        )
        return render(request, self.template_name, context)

    def _handle_delete(self, request):
        form = self.delete_form_class(request.POST)
        if form.is_valid():
            user_principal_name = form.cleaned_data["user_principal_name"]
            method_id = form.cleaned_data["method_id"]
            method_type = form.cleaned_data["method_type"]
            method_label, _ = self.DELETE_HANDLERS.get(
                method_type, (method_type, None)
            )

            try:
                self._delete_authentication_method(
                    user_principal_name, method_id, method_type
                )
                messages.success(
                    request,
                    f"{method_label} authentication method removed for {user_principal_name}.",
                )
            except GraphAPIError as exc:
                messages.error(request, str(exc))

            query = urlencode({"userPrincipalName": user_principal_name})
            return redirect(f"{reverse('mfa-reset')}?{query}")

        messages.error(request, "Invalid delete request.")
        user_principal_name = request.POST.get("user_principal_name", "").strip()
        if user_principal_name:
            query = urlencode({"userPrincipalName": user_principal_name})
            return redirect(f"{reverse('mfa-reset')}?{query}")
        return redirect(reverse("mfa-reset"))

    def _fetch_authentication_methods(self, user_principal_name):
        try:
            data, status_code = execute_list_user_authentication_methods(
                user_principal_name
            )
        except RequestException as exc:
            raise GraphAPIError(f"Unable to contact Microsoft Graph: {exc}") from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise GraphAPIError(f"Unexpected error contacting Microsoft Graph: {exc}") from exc

        if status_code != 200:
            error_detail = self._extract_graph_error(data)
            raise GraphAPIError(
                error_detail
                or f"Microsoft Graph returned status {status_code} when fetching methods."
            )

        if not isinstance(data, dict):
            raise GraphAPIError("Received an unexpected response from Microsoft Graph.")

        return data.get("value", [])

    def _delete_authentication_method(
        self, user_principal_name, method_id, method_type
    ):
        handler_entry = self.DELETE_HANDLERS.get(method_type)
        if not handler_entry:
            raise GraphAPIError("Deletion is not supported for this authentication method.")

        _, handler = handler_entry
        try:
            response, status_code = handler(user_principal_name, method_id)
        except RequestException as exc:
            raise GraphAPIError(f"Unable to contact Microsoft Graph: {exc}") from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise GraphAPIError(f"Unexpected error contacting Microsoft Graph: {exc}") from exc

        if status_code not in {200, 202, 204}:
            error_detail = self._extract_response_error(response)
            raise GraphAPIError(
                error_detail
                or f"Microsoft Graph returned status {status_code} while deleting the method."
            )

    def _transform_methods(self, methods):
        transformed = []
        for method in methods:
            method_type = method.get("@odata.type", "Unknown")
            method_label, _ = self.DELETE_HANDLERS.get(method_type, (method_type, None))
            created_display = self._format_datetime(method.get("createdDateTime"))

            details = []
            for key, value in method.items():
                if key == "@odata.type":
                    continue
                display_value = created_display if key == "createdDateTime" else value
                if display_value in (None, ""):
                    display_value = "N/A"
                details.append((key, display_value))

            transformed.append(
                {
                    "id": method.get("id", ""),
                    "type_key": method_type,
                    "type_label": method_label,
                    "details": details,
                    "created_display": created_display,
                    "can_delete": method_type in self.DELETE_HANDLERS,
                }
            )

        return transformed

    def _format_datetime(self, datetime_string):
        if not datetime_string:
            return None
        parsed = parse_datetime(datetime_string)
        if not parsed:
            return datetime_string
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, timezone.get_default_timezone())
        local_dt = timezone.localtime(parsed)
        return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")

    def _extract_graph_error(self, error_data):
        if isinstance(error_data, dict):
            error = error_data.get("error")
            if isinstance(error, dict):
                code = error.get("code")
                message = error.get("message")
                if code and message:
                    return f"{code}: {message}"
                return message or code
            message = error_data.get("message")
            if message:
                return message
        return ""

    def _extract_response_error(self, response):
        if response is None:
            return "No response received from Microsoft Graph."
        try:
            data = response.json()
        except ValueError:
            return getattr(response, "text", "") or "Microsoft Graph returned an error without details."
        return self._extract_graph_error(data)



















































class ActiveDirectoryCopilotView(BaseView):
    form_class = LargeTextAreaForm
    template_name = "myview/active-directory-copilot.html"
    def get(self, request, **kwargs):
        form = self.form_class()
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    
