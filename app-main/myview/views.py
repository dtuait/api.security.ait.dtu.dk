from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.shortcuts import render
from django.shortcuts import render
from .forms import UserLookupForm
from .models import ADGroupAssociation
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

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class BaseView(View):
    require_login = True  # By default, require login for all views inheriting from BaseView
    base_template = "myview/base.html"

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
        context = {
            'base_template': self.base_template,
            'git_branch': branch,
            'git_commit': commit,
            'is_superuser': self.request.user.is_superuser,
        }

        return context

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.base_template, context)





class AjaxView(BaseView):

    def post(self, request, *args, **kwargs):
        # Extract an 'action' parameter from the POST request to determine which method to call
        action = request.POST.get('action')

        # Check if the action matches one of your AJAX methods
        if action == 'sync_ad_groups':

            if request.user.is_superuser:
                return self.sync_ad_groups(request)
            else:
                # Return an error message if the user is not a superuser
                return JsonResponse({'error': "You need superuser privileges to perform this action."}, status=403)
        elif action == 'create_custom_token':
            if request.user.is_authenticated:
                return self.create_custom_token(request)
            




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

            path = request.POST.get('path')

    
            # logger.info(f"Session data before setting ad_groups: {request.session.items()}")

            request.session['ajax_change_form_update_form_ad_groups'] = ad_groups

            # logger.info(f"Session data after setting ad_groups: {request.session.items()}")
                    
            request.session.save()

            # reload the page
            # return redirect(path) # '/admin/myview/endpoint/1/change/'


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

        user.generate_new_custom_token()
        token = Token.objects.get(user=user)
        
        return JsonResponse({'custom_token': token.key})















class FrontpagePageView(BaseView):
    template_name = "myview/frontpage.html"

    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        return render(request, self.template_name, context)










class MFAResetPageView(BaseView):
    form_class = UserLookupForm
    template_name = "myview/mfa-reset.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
        


