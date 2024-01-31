from django.shortcuts import redirect, render
from django.views import View
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .services import generate_custom_api_token

# Create your views here.


class BaseView(View):
    base_template = "myview/base.html"

    def get_context_data(self, **kwargs):
        context = {
            'base_template': self.base_template,
            # Other common context variables...
        }
        return context
    
    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.base_template, context)


class FrontpagePageView(BaseView):
    template_name = "myview/frontpage.html"

    # is user logged in?
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            token = Token.objects.filter(user=request.user).first()

            context = super().get_context_data(**kwargs)
            context['user'] = request.user
            context['token'] = token.key if token else None  # Pass the token key to the template context if it exists, otherwise pass None

            return render(request, self.template_name, context)
        else:
            return redirect('cas_ng_login')


# @api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_api_token(request):

    generate_custom_api_token(request=request, username=request.user.username)
    
    token, created = Token.objects.get_or_create(user=request.user)
    return JsonResponse({'token': token.key})



# @api_view(['POST'])
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

