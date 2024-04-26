from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View
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
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

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

    # At this point the user has been authenticated and the token has been acquired
    if 'access_token' in token_response:
        access_token = token_response['access_token']
        
        # run validate_user() function return django user object or None, if user is not authenticated
        # validate_user(access_token)




        # Use the access token to make a request to the Microsoft Graph API
        graph_api_endpoint = 'https://graph.microsoft.com/v1.0/me/?$select=onPremisesImmutableId,userPrincipalName'
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
            user_principal_name = user_data.get('userPrincipalName')
            on_premises_immutable_id = user_data.get('onPremisesImmutableId')
            
            from .scripts.validate_user import validate_user

            is_synced = validate_user(user_principal_name=user_principal_name, on_premises_immutable_id=on_premises_immutable_id)
            


            if not is_synced:
                # Return HTTP response if the Azure user account is not synced with the AD account.
                return HttpResponse(
                    "You are not authenticated because the Azure user with which you have logged in does not have a synced AD account. Please log in using a DTU email account, such as user@dtu.dk, afos@dtu.dk, or dast@dtu.dk. For assistance, please contact vicre@dtu.dk.",
                    status=403
                )

            from .scripts.user_have_onpremises_adm_account import user_have_onpremises_adm_account
            user_have_onpremises_adm_account = user_have_onpremises_adm_account(user_principal_name)

            if not user_have_onpremises_adm_account:
                # Construct the dynamic part of the message based on user's principal name.
                adm_account_suffix = user_principal_name.split('@')[0]
                return HttpResponse(
                    f"You are not authenticated because the Azure user with which you have logged in does not have an on-premises admin account. The account adm-{adm_account_suffix}-* does not appear to exist in Active Directory. This restriction is in place to allow only IT staff to access this application. If you believe this is an error or need access, please contact vicre@dtu.dk.",
                    status=403
                )
            
            user, created = User.objects.get_or_create(username=user_principal_name.split('@')[0])
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            if user.is_superuser:
                return HttpResponseRedirect(reverse('admin:index'))
            else:
                return redirect('/myview/frontpage/')
            
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



# # Properply deprecated
# from myview.models import ADGroupAssociation
# def sync_user_ad_groups(user, ad_groups, sync_ad_group_members=False):
#     for distinguished_name in ad_groups[0]['memberOf']:
#         # Try to find the group in the ADGroupAssociation model
#         try:
#             print(distinguished_name)
#             group = ADGroupAssociation.objects.get(distinguished_name=distinguished_name)
#             # Check if user if member of the group if not run sync ad group members
#             if not user.ad_group_members.filter(cn=group.cn).exists() or sync_ad_group_members == True:
#                 print("User is not a member of the group.")
#                 # Mayne this should be async?
#                 group.sync_ad_group_members()
#                 print("Done syncing group members for group: ", group.cn)
#             else:
#                 print("Skipping sync group members for group: ", group.cn)

#         except ADGroupAssociation.DoesNotExist:
#             print(f"ADGroupAssociation with distinguished_name {distinguished_name} does not exist.")
            
#         except Exception as e:
#             # If the group does not exist, create it
#             print(f"An error occurred: {e}")




















# # @method_decorator(login_required, name='dispatch')
# class AjaxView(View):

#     def post(self, request, *args, **kwargs):
#         # Extract an 'action' parameter from the POST request to determine which method to call
#         action = request.POST.get('action')

#         # Check if the action matches one of your AJAX methods
#         if action == 'get_ad_groups':

#             if request.user.is_superuser:
#                 return self.get_ad_groups(request)
#             else:
#                 # Return an error message if the user is not a superuser
#                 return JsonResponse({'error': "You need superuser privileges to perform this action."}, status=403)

            
#         else:
#             return JsonResponse({'error': 'Invalid AJAX action'}, status=400)


#     def get_ad_groups(self, request):
#         # Get the list of AD groups associated with the user
#         # search for the user in the ADGroupAssociation model
    
        
#         ad_groups = request.user.ad_groups.all()
#         ad_groups_list = [group.name for group in ad_groups]
#         return JsonResponse({'ad_groups': ad_groups_list})