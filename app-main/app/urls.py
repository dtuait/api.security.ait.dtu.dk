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
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from app_mod.views import AdminCasLoginView
import django_cas_ng.views
from myview.views import FrontpagePageView

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
#    permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [

    # redirect '' to 'my-view/frontpage'¨
    # path('', include('myview.urls')),
    # path('', include('myview.urls')),
    # redirect root URL to pubs/publist
    # path('', RedirectView.as_view(url="myview/frontpage/", permanent=True)),
     path('', FrontpagePageView.as_view(), name='frontpage'),

    # admin panel 
    path('admin-3dbLnPXcGL4GLAw2cDgBm6F4LrS5VXTD/', admin.site.urls),
    # path('admin-cas-login/', AdminCasLoginView.as_view(), name='admin-cas-login'),

    # cas login and logout
    path("login/", django_cas_ng.views.LoginView.as_view(), name="cas_ng_login"),
    path("logout/", django_cas_ng.views.LogoutView.as_view(), name="cas_ng_logout"),

    # graph api
    path('', include('graph.urls')),

    # sccm api
    # path('sccm/', include('sccm.urls')),

    # active directory api
    # path('active_directory/', include('active_directory.urls')),

    # playbook api 
    path('playbook/', include('playbook.urls')),

    # panel for 
    path('myview/', include('myview.urls')),



    
    # # # misc api
    # path('misc/', include('misc.urls')),,

    #swagger ui
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # redoc
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


    
    # path('', include('myview.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    