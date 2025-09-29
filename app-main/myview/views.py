from django.shortcuts import render
from django.views import View
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.shortcuts import render
from .forms import LargeTextAreaForm
from .models import Endpoint
import subprocess
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import logging
from datetime import datetime

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

    def get_git_info(self):
        try:
            branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
            last_updated = subprocess.check_output(['git', 'log', '-1', '--format=%cd']).decode('utf-8').strip()

            # Parse the last_updated date string and reformat it
            last_updated_dt = datetime.strptime(last_updated, '%a %b %d %H:%M:%S %Y %z')
            last_updated_formatted = last_updated_dt.strftime('%H:%M %d-%m-%Y')
        except subprocess.CalledProcessError:
            # Default values if git commands fail
            branch = "unknown"
            commit = "unknown"
            last_updated = "unknown"
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


















































class MFAResetPageView(BaseView):

    template_name = "myview/mfa-reset.html"

    def get(self, request, *args, **kwargs):
        if not self.user_has_mfa_reset_access():
            return HttpResponseForbidden("You do not have access to this page.")
        context = super().get_context_data(**kwargs)
        return render(request, self.template_name, context)



















































class ActiveDirectoryCopilotView(BaseView):
    form_class = LargeTextAreaForm
    template_name = "myview/active-directory-copilot.html"
    def get(self, request, **kwargs):
        form = self.form_class()
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    

