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


logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class BaseView(View):
    require_login = True  # By default, require login for all views inheriting from BaseView
    base_template = "myview/base.html"


    def user_has_mfa_reset_access(self):
        required_endpoints = [
            {'method': 'GET', 'path': '/graph/v1.0/get-user/{user}'},
            {'method': 'GET', 'path': '/graph/v1.0/list/{user_id__or__user_principalname}/authentication-methods'},
            {'method': 'DELETE', 'path': '/graph/v1.0/users/{user_id__or__user_principalname}/authentication-methods/{microsoft_authenticator_method_id}'},
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
        except subprocess.CalledProcessError:
            # Default values if git commands fail
            branch = "unknown"
            commit = "unknown"
        return branch, commit

    def get_context_data(self, **kwargs):
        branch, commit = self.get_git_info()
        user_ad_groups = self.request.user.ad_group_members.all()
        user_endpoints = Endpoint.objects.filter(ad_groups__in=user_ad_groups).prefetch_related('ad_groups').distinct()
        user_ad_group_ids = user_ad_groups.values_list('id', flat=True)

        # Filter endpoints to include only user-specific group access information
        filtered_endpoints = []
        for endpoint in user_endpoints:
            # Filter ad_groups to include only those where the user is a member
            filtered_groups = endpoint.ad_groups.filter(members=self.request.user)
            filtered_endpoints.append({
                'method': endpoint.method,
                'path': endpoint.path,
                'ad_groups': filtered_groups,
                'limiter_type': endpoint.limiter_type.name if endpoint.limiter_type else "None",
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

        # for all limiter types check if a group that request.user is member of is associated with the group

        from django.conf import settings
        context = {
            'base_template': self.base_template,
            'git_branch': branch,
            'git_commit': commit,
            'is_superuser': self.request.user.is_superuser,
            'user_endpoints': filtered_endpoints,  # Replace with the filtered list
            'user_ad_groups': user_ad_groups,
            'user_has_mfa_reset_access': self.user_has_mfa_reset_access(),
            'debug': settings.DEBUG,
            'all_limiter_types': associated_limiter_types,
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
    

