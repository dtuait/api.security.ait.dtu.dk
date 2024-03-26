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

@login_required
def cas_director(request):

        try:
            
            if request.user.is_superuser:
                return HttpResponseRedirect(reverse('admin:index'))  # Redirect to admin page
            elif request.user:
                return HttpResponseRedirect('/myview/frontpage/')

            
            HttpResponseRedirect('/myview/only-allowed-for-it-staff/')

        except ImportError:
            print("ADGroupAssociation model is not available for registration in the admin site.")
            HttpResponseRedirect('/myview/only-allowed-for-it-staff/')
        

urlpatterns = [
    # cas login and logout
    path("login/", LoginView.as_view(), name="cas_ng_login"),
    path("login-redirector/", cas_director, name="cas_ng_login_redirector"),
    path("logout/", LogoutView.as_view(), name="cas_ng_logout"),
    path('admin-3dbLnPXcGL4GLAw2cDgBm6F4LrS5VXTD/', admin.site.urls),
    
    # myview
    path('', RedirectView.as_view(url="myview/frontpage/", permanent=True)),
    path('myview/', include('myview.urls')),

    # graph api
    path('', include('graph.urls')),

    # playbook api 
    path('playbook/', include('playbook.urls')),

    # sccm api
    # path('sccm/', include('sccm.urls')),

    # active directory api
    # path('active_directory/', include('active_directory.urls')),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    