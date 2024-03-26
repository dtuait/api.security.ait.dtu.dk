from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import msal
import os
from dotenv import load_dotenv
import requests
from msal import ConfidentialClientApplication
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login, logout
dotenv_path = '/usr/src/project/.devcontainer/.env'
load_dotenv(dotenv_path=dotenv_path)

def msal_callback(request):
    # The state should be passed to the authorization request and validated in the response.
    if 'code' not in request.GET:
        return HttpResponse("Error: code not received.", status=400)

    code = request.GET['code']
    state = request.GET.get('state')

    # Validate the state parameter (if you passed one in the authorization request)

    # MSAL Config
    tenant_id = os.getenv('AZURE_TENANT_ID')
    authority_url = f'https://login.microsoftonline.com/{tenant_id}'
    client_id = os.getenv('AIT_SOC_MSAL_VICRE_CLIENT_ID')
    client_secret = os.getenv('AIT_SOC_MSAL_VICRE_MSAL_SECRET_VALUE')
    redirect_uri = 'https://api.security.ait.dtu.dk/auth/callback'  # Updated

    # Initialize the MSAL confidential client
    client_app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority_url,
        client_credential=client_secret,
    )

    # Acquire a token by authorization code from Azure AD's token endpoint
    token_response = client_app.acquire_token_by_authorization_code(
        code,
        scopes=['User.Read'],  # You can add other scopes/permissions
        redirect_uri=redirect_uri
    )

    if 'access_token' in token_response:
        access_token = token_response['access_token']
        
        # Use the access token to make a request to the Microsoft Graph API
        graph_api_endpoint = 'https://graph.microsoft.com/v1.0/me/'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Make the GET request to the Graph API to get user details
        graph_response = requests.get(graph_api_endpoint, headers=headers)
        
        if graph_response.status_code == 200:
            # Successful request to the Graph API
            user_data = graph_response.json()
            # Extract the preferred username (which could be the user's email)
            username = user_data.get('userPrincipalName')

            # remove the @dtudk.onmicrosoft.com from the username
            username = username.split('@')[0]

            # check of the username starts with 'adm-' or contains -adm-
            if username.startswith('adm-') or '-adm-' in username:
                from django.contrib.auth.backends import ModelBackend

                # After getting or creating the user
                user, created = User.objects.get_or_create(username=username)

                # Specify the backend explicitly
                user.backend = 'django.contrib.auth.backends.ModelBackend'

                # Now log the user in
                login(request, user)

                if user.is_superuser:
                    return HttpResponseRedirect(reverse('admin:index'))
                else:
                    return redirect('/myview/frontpage/')
            
            else:
                
                return HttpResponse("Error: User not authorized. You need to login with a user that starts with adm-", status=403)
            

        else:
            # Handle failure or show an error message to the user
            return HttpResponse("Error: failed to retrieve user information.", status=graph_response.status_code)
    else:
        # Handle failure or show an error message to the user
        return HttpResponse("Error: failed to retrieve access token.", status=400)
    


@login_required
def msal_director(request):      
    try:
        
        if request.user.is_superuser:
            return HttpResponseRedirect(reverse('admin:index'))  # Redirect to admin page
        elif request.user:
            return HttpResponseRedirect('/myview/frontpage/')
    
        HttpResponseRedirect('/myview/only-allowed-for-it-staff/')

    except ImportError:
        print("ADGroupAssociation model is not available for registration in the admin site.")
        HttpResponseRedirect('/myview/only-allowed-for-it-staff/') 



def msal_login(request):
    # Initialize the MSAL Confidential Client Application with the settings from your configuration
    # print("Client Secret from env:", os.getenv('AIT_SOC_MSAL_VICRE_CLIENT_SECRET'))
    client_app = ConfidentialClientApplication(
        settings.AZURE_AD['CLIENT_ID'],
        authority=settings.AZURE_AD['AUTHORITY'],
        client_credential=settings.AZURE_AD['CLIENT_SECRET'],
    )

    # Get the URL of the Microsoft login page
    auth_url = client_app.get_authorization_request_url(
        scopes=settings.AZURE_AD['SCOPE'],
        redirect_uri=settings.AZURE_AD['REDIRECT_URI']
    )
    
    # Redirect to the Microsoft login page
    return redirect(auth_url)

def msal_logout(request):
    logout(request)
    response = redirect('https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri=https://api.security.ait.dtu.dk/myview/frontpage/')
    response.delete_cookie('csrftoken')
    return response