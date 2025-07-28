# app_mod/authentication.py

from rest_framework.authentication import TokenAuthentication
from .models import CustomToken

class CustomTokenAuthentication(TokenAuthentication):
    model = CustomToken