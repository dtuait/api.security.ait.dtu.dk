from django.urls import path
from .views import (
    BreachedAccountView,
    BreachesView,
    DataClassesView,
    LatestBreachView,
    BreachDetailView,
    PasteAccountView,
    SubscriptionStatusView,
)

urlpatterns = [
    path("v1.0/breachedaccount/<str:email>", BreachedAccountView.as_view(), name="breached-account"),
    path("v1.0/breaches", BreachesView.as_view(), name="breaches"),
    path("v1.0/dataclasses", DataClassesView.as_view(), name="dataclasses"),
    path("v1.0/latestbreach", LatestBreachView.as_view(), name="latest-breach"),
    path("v1.0/breach/<str:name>", BreachDetailView.as_view(), name="breach-detail"),
    path("v1.0/pasteaccount/<str:account>", PasteAccountView.as_view(), name="paste-account"),
    path("v1.0/subscription/status", SubscriptionStatusView.as_view(), name="subscription-status"),
]
