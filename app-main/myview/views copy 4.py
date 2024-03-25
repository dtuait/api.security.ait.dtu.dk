from django.shortcuts import redirect, render
from django.views import View
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .services import generate_custom_api_token
from django.shortcuts import render
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.http import HttpResponseForbidden

# Create your views here.
from django.shortcuts import render
from .forms import UserLookupForm
# from .models import User  # Ensure you import the correct User model
from .models import ADGroupAssociation
from django.http import HttpResponse
from graph.services import execute_get_user as get_user, execute_list_user_authentication_methods as list_user_authentication_methods, execute_delete_user_authentication_method as delete_authentication_method   
import subprocess
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

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
            return self.sync_ad_groups(request)
        elif action == 'reset_mfa':
            return self.reset_mfa(request)
        else:
            return JsonResponse({'error': 'Invalid AJAX action'}, status=400)

    def reset_mfa(self, request):
        # Your logic here
        return JsonResponse({'success': True})

    def sync_ad_groups(self, request):
        # Your logic here
        result = ADGroupAssociation.sync_ad_groups(None)
        
        return JsonResponse({'success': result})



class FrontpagePageView(BaseView):
    template_name = "myview/frontpage.html"


    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)

        # from myview.models import ADGroupAssociation
        # ADGroupAssociation.sync_ad_groups(None)

        # Your view logic here, accessible without login
        return render(request, self.template_name, context)

















# # views.py
# from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
# from django.views import View
# from .forms import UserLookupForm
# # Import other necessary modules and models

# class MFAResetPageView(BaseView):
#     form_class = UserLookupForm
#     template_name = "myview/mfa-reset.html"

#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         context = super().get_context_data(**kwargs)
#         context['form'] = form
#         return render(request, self.template_name, context)
#         # return render(request, self.template_name, {'form': form})


    
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             try:                
#                 # Assuming 'request.user' is the logged-in User instance
#                 user_profile = request.user

#                 # Check if the user has access to the endpoint


#                 if not user_profile.has_endpoint_access('/v1.0/graph/get-user/{user}', 'get') and not request.user.is_superuser:
#                     return HttpResponseForbidden("You do not have access to this endpoint. /v1.0/graph/get-user/{user}")
            
#                 # return HttpResponse(f"First Name: {user.first_name}, Last Name: {user.last_name}")


#                 if '@' in username:
#                     user_principal_name = username
#                 else:
#                     user_principal_name = f"{username}@dtu.dk"
#                 user_principal_object, http_status_code = get_user(user_principal_name)

#                 # get authentication methods

#                 if not user_profile.has_endpoint_access('/v1.0/graph/list/{user_id__or__user_principalname}/authentication-methods', 'get') and not request.user.is_superuser:
#                     return HttpResponseForbidden("You do not have access to this endpoint. /v1.0/graph/list/{user_id__or__user_principalname}/authentication-methods")

#                 authentication_methods = list_user_authentication_methods(user_principal_object['id'])

#                 # Assuming authentication_methods is your tuple
#                 # Extract the dictionary containing your data
#                 auth_methods_data = authentication_methods[0]  # This is the dictionary

#                 # Now, filter out the unwanted objects from the 'value' list
#                 filtered_auth_methods = [method for method in auth_methods_data['value'] if method.get('@odata.type') != "#microsoft.graph.passwordAuthenticationMethod"]

#                 # Replace the original 'value' list with the filtered list
#                 auth_methods_data['value'] = filtered_auth_methods

#                 # If you need to work with the tuple structure again, you can reconstruct it
#                 authentication_methods = (auth_methods_data, authentication_methods[1])

#                 # create an object that contains the user principal object and the authentication methods
#                 user_principal_object['authentication_methods'] = authentication_methods

#                 # return the user principal object
#                 return JsonResponse(user_principal_object)

#             except User.DoesNotExist:
#                 return JsonResponse("Internal Server Error", status=500)
            
#         else:
#             context = super().get_context_data(**kwargs)
#             context['form'] = form
#             return render(request, self.template_name, context)



    def delete(self, request, user_principal_id, authentication_id, *args, **kwargs):
        # Here you'll handle the deletion
        try:
            # user_profile = UserProfile.objects.get(user=request.user)
            # Assuming you have access to request.user and the method to validate access
            if not self.user_has_permission(request, user_principal_id):
                return HttpResponseForbidden("You do not have permission to delete this method.")

            # Perform the deletion logic here
            # For example:
            # AuthenticationMethod.objects.get(id=method_id).delete()
            response, status_code = delete_authentication_method(user_principal_id, authentication_id)
            if status_code != 204:
                return JsonResponse({'status': 'error', 'message': 'Failed to delete authentication method.'}, status=500)
            

            return JsonResponse({'status': 'success', 'message': 'Authentication method deleted successfully.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def user_has_permission(self, request, user_principal_id):
        user_profile = request.user
        # Implement your logic to check if the user has permission to delete the given method
        if not user_profile.has_endpoint_access('/v1.0/graph/delete-mfa/{user}', 'delete') and not request.user.is_superuser:
            return False
        return True  # Placeholder, implement your actual logic

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'delete':
            return self.delete(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def generate_api_token(request):

#     generate_custom_api_token(request=request, username=request.user.username)
    
#     token, created = Token.objects.get_or_create(user=request.user)
#     return JsonResponse({'token': token.key})



# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def regenerate_api_token(request):
#     try:
#         # Get the existing token
#         token = Token.objects.get(user=request.user)
#         # Delete the old token
#         token.delete()
#     except Token.DoesNotExist:
#         pass
    
#     generate_custom_api_token(request=request, username=request.user.username)
    
#     token, created = Token.objects.get_or_create(user=request.user)
#     return JsonResponse({'token': token.key})












































































# class MFAResetPageView(BaseView):
#     template_name = "myview/mfa-reset.html"


#     def get(self, request, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Your view logic here, accessible without login
#         return render(request, self.template_name, context)













# def mfa_reset(request):
#     if request.method == 'POST':
#         form = UserLookupForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             # Assuming you have a method to fetch user info. Adjust as necessary.
#             try:
#                 user = User.objects.get(username=username)
#                 first_name = user.first_name
#                 last_name = user.last_name
#                 # Handle the response as you see fit. This is a simple example.
#                 return HttpResponse(f"First Name: {first_name}, Last Name: {last_name}")
#             except User.DoesNotExist:
#                 return HttpResponse("User not found.")
#     else:
#         form = UserLookupForm()
#     return render(request, 'myapp/mfa-reset.html', {'form': form})












# class MFAResetPageView(BaseView):
#     form_class = UserLookupForm
#     template_name = "myview/mfa-reset.html"

#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         context = super().get_context_data(**kwargs)
#         context['form'] = form
#         return render(request, self.template_name, context)
#         # return render(request, self.template_name, {'form': form})

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             try:                
#                 # Assuming 'request.user' is the logged-in User instance
#                 user_profile = UserProfile.objects.get(user=request.user)

#                 # Check if the user has access to the endpoint


#                 if not user_profile.has_endpoint_access('/v1.0/graph/get-user/{user}', 'get') and not request.user.is_superuser:
#                     return HttpResponseForbidden("You do not have access to this endpoint. /v1.0/graph/get-user/{user}")
            
#                 # return HttpResponse(f"First Name: {user.first_name}, Last Name: {user.last_name}")


#                 if '@' in username:
#                     user_principal_name = username
#                 else:
#                     user_principal_name = f"{username}@dtu.dk"
#                 user_principal_object, http_status_code = get_user(user_principal_name)

#                 # get authentication methods

#                 if not user_profile.has_endpoint_access('/v1.0/graph/list/{user_id__or__user_principalname}/authentication-methods', 'get') and not request.user.is_superuser:
#                     return HttpResponseForbidden("You do not have access to this endpoint. /v1.0/graph/list/{user_id__or__user_principalname}/authentication-methods")

#                 authentication_methods = list_user_authentication_methods(user_principal_object['id'])

#                 # Assuming authentication_methods is your tuple
#                 # Extract the dictionary containing your data
#                 auth_methods_data = authentication_methods[0]  # This is the dictionary

#                 # Now, filter out the unwanted objects from the 'value' list
#                 filtered_auth_methods = [method for method in auth_methods_data['value'] if method.get('@odata.type') != "#microsoft.graph.passwordAuthenticationMethod"]

#                 # Replace the original 'value' list with the filtered list
#                 auth_methods_data['value'] = filtered_auth_methods

#                 # If you need to work with the tuple structure again, you can reconstruct it
#                 authentication_methods = (auth_methods_data, authentication_methods[1])

#                 # create an object that contains the user principal object and the authentication methods
#                 user_principal_object['authentication_methods'] = authentication_methods

#                 # return the user principal object
#                 return JsonResponse(user_principal_object)
            

#                 # return HttpResponse(f"Displayname: {user_principal_object['displayName']}")
#                 # context = super().get_context_data(**kwargs)
#                 # context['form'] = form
#                 # # context['user_principal_object'] = user_principal_object
#                 # # context['authentication_methods'] = authentication_methods
#                 # return render(request, self.template_name, context)
#             except User.DoesNotExist:
#                 return JsonResponse("Internal Server Error", status=500)
#         else:
#             context = super().get_context_data(**kwargs)
#             context['form'] = form
#             return render(request, self.template_name, context)


