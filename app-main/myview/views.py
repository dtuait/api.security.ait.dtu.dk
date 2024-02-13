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


    # def get(self, request, **kwargs):
    #     if request.user.is_authenticated:
    #         token = Token.objects.filter(user=request.user).first()

    #         context = super().get_context_data(**kwargs)
    #         context['user'] = request.user
    #         context['token'] = token.key if token else None  # Pass the token key to the template context if it exists, otherwise pass None

    #         return render(request, self.template_name, context)
    #     else:
    #         return redirect('cas_ng_login')
    

class FrontpagePageView(BaseView):
    template_name = "myview/frontpage.html"


    def get(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        # Your view logic here, accessible without login
        return render(request, self.template_name, context)


    # # is user logged in?
    # def get(self, request, **kwargs):
    #     if request.user.is_authenticated:
    #         token = Token.objects.filter(user=request.user).first()

    #         context = super().get_context_data(**kwargs)
    #         context['user'] = request.user
    #         context['token'] = token.key if token else None  # Pass the token key to the template context if it exists, otherwise pass None

    #         return render(request, self.template_name, context)
    #     else:
    #         return redirect('cas_ng_login')







# schema_view = get_schema_view(
#    openapi.Info(
#       title="API",
#       default_version='v1',
#       description="A simple API",
#       terms_of_service="https://www.google.com/policies/terms/",
#       contact=openapi.Contact(email="vicre@dtu.dk"),
#       license=openapi.License(name="BSD License"),
#    ),
#    public=True,
#    permission_classes=(AllowAny,),
# )


# # # @permission_classes([IsAuthenticated])
# # from django.urls import reverse

# # def custom_swagger_view(request):
# #     # Assuming you have a URL named 'schema-json' that serves your OpenAPI schema
# #     schema_url = request.build_absolute_uri(reverse('schema-json'))
# #     return render(request, 'custom_swagger.html', {'schema_url': schema_url})

# from django.urls import reverse

# def custom_swagger_view(request):
#     template_name = "myview/custom_swagger.html"
#     # Build the URL to the Swagger UI
#     schema_url = reverse('myview/schema-swagger-ui')
#     return render(request, template_name, {'schema_url': schema_url})

# # def custom_swagger_view(request):
# #     schema_url = schema_view.without_ui(cache_timeout=0)
# #     return render(request, 'custom_swagger.html', {'schema_url': schema_url.url})













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

