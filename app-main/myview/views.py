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

# Create your views here.


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

