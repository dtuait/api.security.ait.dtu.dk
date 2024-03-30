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
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django_cas_ng.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import RedirectView
from msal import ConfidentialClientApplication
from django.shortcuts import redirect
from .views import msal_callback, msal_login, msal_director, msal_logout
from dotenv import load_dotenv
import os
from django.views.static import serve
from django.urls import re_path
dotenv_path = '/usr/src/project/.devcontainer/.env'
load_dotenv(dotenv_path=dotenv_path)
from .views import AjaxView



urlpatterns = [
    path("login/", msal_login, name="msal_login"),
    path('auth/callback/', msal_callback, name='msal_callback'),
    path("login-redirector/", msal_director, name="msal_login_redirector"),
    path("logout/", msal_logout, name="msal_logout"),

    #  favicon.ico
    re_path(r'^favicon\.ico$', serve, {
    'path': 'myview/img/favicon.ico',
    'document_root': settings.STATIC_ROOT,
    }),

    path('admin/', admin.site.urls, name='admin-panel'),
    
    # myview
    path('', RedirectView.as_view(url="myview/frontpage/", permanent=True)),
    path('myview/', include('myview.urls')),

    # graph api
    path('', include('graph.urls')),

    # playbook api 
    path('playbook/', include('playbook.urls')),

    # active directory api
    path('', include('active_directory.urls')),

    # path('admin/app/ajax/', AjaxView.as_view(), name='admin-app-ajax'),



]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    