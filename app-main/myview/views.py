from django.shortcuts import render
from django.views import View
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework.authtoken.models import Token
from django.shortcuts import render
from django.shortcuts import render
from .forms import UserLookupForm, LargeTextAreaForm
from .models import ADGroupAssociation, Endpoint
import subprocess
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from active_directory.scripts.active_directory_query import active_directory_query
from ldap3 import ALL_ATTRIBUTES
from rest_framework.response import Response
import json
from django.shortcuts import redirect
import logging
from django.contrib.contenttypes.models import ContentType
from .models import LimiterType, IPLimiter, ADOrganizationalUnitLimiter

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





class AjaxView(BaseView):

    def post(self, request, *args, **kwargs):
        # Extract an 'action' parameter from the POST request to determine which method to call
        action = request.POST.get('action')

        if action == 'clear_my_ad_group_cached_data':
            # return dummy response - cache has been cleared
            from django.core.cache import cache
            try:
                cache.clear()
                return JsonResponse({'success': 'Cache cleared'})
            except Exception as e:
                return JsonResponse({'error': str(e)})



        elif action == 'create_custom_token':
            if request.user.is_authenticated:
                return self.create_custom_token(request)
            


        elif action == 'copilot-chatgpt-basic':
            if request.user.is_authenticated:
                # return not implemented yet status 200
                content = request.POST.get('content')
                user = json.loads(content)

                from chatgpt_app.scripts.openai_basic import get_openai_completion

                message = get_openai_completion(
                    system="You return 1 ldap3 query at a time. Give me a ldap3 query that returns user name vicre >> (sAMAccountName=vicre). Do not explain the query, just provide it.",
                    user=user['user']
                )

                return JsonResponse({'message': message.content})

            
            




        elif action == 'active_directory_query':
            # Extract the parameters from the POST request
            base_dn = request.POST.get('base_dn')
            search_filter = request.POST.get('search_filter')
            search_attributes = request.POST.get('search_attributes')
            search_attributes = search_attributes.split(',') if search_attributes else ALL_ATTRIBUTES
            limit = request.POST.get('limit')
            
            if limit is not None:
                limit = int(limit)
                
            # Perform the active directory query
            result = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=limit)
            # return Response(result)
            return JsonResponse(result, safe=False)
        

        



        elif action == 'ajax_change_form_update_form_ad_groups':
            # Extract ad_groups = [] from the POST request
            ad_groups = request.POST.getlist('ad_groups')
            # convert ad_groups[0] into a list. The data is JSON encoded in the POST request
            ad_groups = json.loads(ad_groups[0])

            request.session['ajax_change_form_update_form_ad_groups'] = ad_groups

            # logger.info(f"Session data after setting ad_groups: {request.session.items()}")
            request.session.save()

            # reload the page
            # return redirect(path) # '/admin/myview/endpoint/1/change/'


            return JsonResponse({'success': 'Form updated'})


        elif action == 'ajax__search_form__add_new_organizational_unit':
            
            try:
                # Extract the parameters from the POST request
                base_dn = 'DC=win,DC=dtu,DC=dk'
                distinguished_name = request.POST.get('distinguished_name')
                search_filter = f'(&(objectClass=organizationalUnit)(distinguishedName={distinguished_name}))'
                search_attributes = 'distinguishedName,canonicalName'
                search_attributes = search_attributes.split(',') if search_attributes else ALL_ATTRIBUTES
                limit = 1

                if limit is not None:
                    limit = int(limit)

                # Perform the active directory query
                organizational_unit = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=limit)

                # If len(organizational_unit) != 1 then return error JsonResponse
                if len(organizational_unit) != 1:
                    raise ValueError("No match found for the distinguished name.")

                # Get or create a new ADOrganizationalUnitLimiter
                from .models import ADOrganizationalUnitLimiter
                ou_limiter, created = ADOrganizationalUnitLimiter.objects.get_or_create(
                    canonical_name=organizational_unit[0]['canonicalName'][0],
                    distinguished_name=organizational_unit[0]['distinguishedName'][0]
                )

            
                return JsonResponse({'success': 'New organizational unit created'}, status=201)


            except Exception as e:
                from django.conf import settings
                if settings.DEBUG:
                    return JsonResponse({'error': str(e)}, status=500)
                else:
                    return JsonResponse({'error': 'Internal server error'}, status=500)


    
        elif action == 'ajax_change_form_update_form_ad_ous':
            # Extract ad_ous from the POST request
            ad_ous = request.POST.getlist('ad_ous')
            # convert ad_ous[0] into a list. The data is JSON encoded in the POST request
            ad_ous = json.loads(ad_ous[0])

            # logger.info(f"Session data before setting ad_ous: {request.session.items()}")

            request.session['ajax_change_form_update_form_ad_ous'] = ad_ous

            # logger.info(f"Session data after setting ad_ous: {request.session.items()}")

            request.session.save()

            return JsonResponse({'success': 'Form updated'})

            
        else:
            return JsonResponse({'error': 'Invalid AJAX action'}, status=400)



    def sync_ad_groups(self, request):
        # Your logic here
        result = ADGroupAssociation.sync_ad_groups(None)
        
        return JsonResponse({'success': result})


    def create_custom_token(self, request):
        user = User.objects.get(username=request.user.username)
        # Generate random string of length 255        
        token = user.generate_new_custom_token()        
        return JsonResponse({'custom_token': token.key})















@method_decorator(login_required, name='dispatch')
class FrontpagePageView(BaseView):
    template_name = "myview/frontpage.html"
    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        return render(request, self.template_name, context)








class MFAResetPageView(BaseView):
    form_class = UserLookupForm
    template_name = "myview/mfa-reset.html"

    def get(self, request, *args, **kwargs):
        if not self.user_has_mfa_reset_access():
            return HttpResponseForbidden("You do not have access to this page.")
        form = self.form_class()
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)



class ActiveDirectoryCopilotView(BaseView):
    form_class = LargeTextAreaForm
    template_name = "myview/active-directory-copilot.html"
    def get(self, request, **kwargs):
        form = self.form_class()
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
    

