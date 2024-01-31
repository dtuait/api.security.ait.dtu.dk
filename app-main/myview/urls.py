from django.urls import include, path, reverse_lazy
from django.contrib.auth import views as auth_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import FrontpagePageView, SwaggerView, generate_api_token, regenerate_api_token, custom_swagger_view, schema_view


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

    # path('', FrontpagePageView.as_view(), name='frontpage'),
    path('frontpage/', FrontpagePageView.as_view(), name='frontpage'),



    path('generate-token/', generate_api_token, name='generate_api_token'),
    path('regenerate-token/', regenerate_api_token, name='regenerate_api_token'),

    # path('base/', views.BaseView.as_view(), name='base'),
    # path('frontpage/', views.FrontPageView.as_view(), name='frontpage'),
    # path('map/', views.MapView.as_view(), name='map'),
    # path('reports/', views.ReportsView.as_view(), name='reports'),
    # path('persons/', views.PersonsView.as_view(), name='persons'),

    # path('report/<int:publication_id>/', views.ReportView.as_view(), name='report'),
    # path('person/<int:person_id>/', views.PersonView.as_view(), name='person'),
    # path('feature/<int:feature_id>/', views.FeatureView.as_view(), name='feature'),
    # path('login/', views.LoginView.as_view(), name='login'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('accounts/logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('frontpage')), name='logout'),

]