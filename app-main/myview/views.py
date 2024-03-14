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
from .models import UserProfile, AccessRequest, EndpointPermission

# Create your views here.
from django.shortcuts import render
from .forms import UserLookupForm
from .models import User  # Ensure you import the correct User model
from django.http import HttpResponse
from graph.services import execute_get_user as get_user

class BaseView(View):
    require_login = True  # By default, require login for all views inheriting from BaseView
    base_template = "myview/base.html"

    def dispatch(self, request, *args, **kwargs):
        # Check if login is required and whether the user is authenticated
        if self.require_login and not request.user.is_authenticated:
            # Redirect unauthenticated users to the login page or a specified URL
            return redirect('cas_ng_login')  # Update 'login_url' to your actual login route
        # Proceed with the normal flow if login is not required or if the user is authenticated
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = {
            'base_template': self.base_template,
            # Other common context variables...
        }
        return context
    
    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.base_template, context)




class CustomSwaggerView(BaseView):
    template_name = "myview/custom_swagger.html"


    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        # Your view logic here, accessible without login
        return render(request, self.template_name, context)

    

class FrontpagePageView(BaseView):
    template_name = "myview/frontpage.html"





class SwaggerView(BaseView):
    template_name = "myview/custom_swagger.html"


    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        # Your view logic here, accessible without login
        return render(request, self.template_name, context)









class FrontpagePageView(BaseView):
    template_name = "myview/frontpage.html"


    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        # Your view logic here, accessible without login
        return render(request, self.template_name, context)







class MFAResetPageView(BaseView):
    form_class = UserLookupForm
    template_name = "myview/mfa-reset.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = super().get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
        # return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:                
                # Assuming 'request.user' is the logged-in User instance
                user_profile = UserProfile.objects.get(user=request.user)

                # Check if the user has access to the endpoint


                if not user_profile.has_endpoint_access('/v1.0/graph/get-user/{user}', 'get') and not request.user.is_superuser:
                    return HttpResponseForbidden("You do not have access to this endpoint.")
            
                # return HttpResponse(f"First Name: {user.first_name}, Last Name: {user.last_name}")
                user_principal_name = f"{username}@dtu.dk"
                user_principal_object, http_status_code = get_user(user_principal_name)
                

                return HttpResponse(f"Displayname: {user_principal_object['displayName']}")
            except User.DoesNotExist:
                return HttpResponse("User not found.")
        else:
            context = super().get_context_data(**kwargs)
            context['form'] = form
            return render(request, self.template_name, context)

# class MFAResetPageView(BaseView):
#     template_name = "myview/mfa-reset.html"


#     def get(self, request, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Your view logic here, accessible without login
#         return render(request, self.template_name, context)




def mfa_reset(request):
    if request.method == 'POST':
        form = UserLookupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            # Assuming you have a method to fetch user info. Adjust as necessary.
            try:
                user = User.objects.get(username=username)
                first_name = user.first_name
                last_name = user.last_name
                # Handle the response as you see fit. This is a simple example.
                return HttpResponse(f"First Name: {first_name}, Last Name: {last_name}")
            except User.DoesNotExist:
                return HttpResponse("User not found.")
    else:
        form = UserLookupForm()
    return render(request, 'myapp/mfa-reset.html', {'form': form})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_api_token(request):

    generate_custom_api_token(request=request, username=request.user.username)
    
    token, created = Token.objects.get_or_create(user=request.user)
    return JsonResponse({'token': token.key})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_api_token(request):
    try:
        # Get the existing token
        token = Token.objects.get(user=request.user)
        # Delete the old token
        token.delete()
    except Token.DoesNotExist:
        pass
    
    generate_custom_api_token(request=request, username=request.user.username)
    
    token, created = Token.objects.get_or_create(user=request.user)
    return JsonResponse({'token': token.key})

