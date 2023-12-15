"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from app_mod.views import AdminCasLoginView
import django_cas_ng.views

schema_view = get_schema_view(
   openapi.Info(
      title="API",
      default_version='v1',
      description="A simple API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="vicre@dtu.dk"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # admin panel 
    path('admin/', admin.site.urls),
    path('admin-cas-login/', AdminCasLoginView.as_view(), name='admin-cas-login'),

    # cas login and logout
    path("login/", django_cas_ng.views.LoginView.as_view(), name="cas_ng_login"),
    path("logout/", django_cas_ng.views.LogoutView.as_view(), name="cas_ng_logout"),

    # graph api
    path('azure/', include('azure.urls')),

    # sccm api
    path('', include('sccm.urls')),

    # active directory api
    path('', include('active_directory.urls')),

    # # misc api
    path('misc/', include('misc.urls')),

    # playbook
    path('playbook/', include('playbook.urls')),

    #swagger ui
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # redoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # panel for 
    path('my-view/', include('myview.urls')),

    # redirect index to myview
    path('', include('myview.urls')),

]