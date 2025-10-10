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
import urllib.parse
import time
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_control
from myview.models import UserLoginLog

logger = logging.getLogger(__name__)





def _get_client_ip(request):
    """Best-effort extraction of the client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')











































def msal_callback(request):
    # The state should be passed to the authorization request and validated in the response.
    if 'code' not in request.GET:
        try:
            from myview.models import UserActivityLog

            UserActivityLog.log_login(
                username=request.GET.get('login_hint', ''),
                request=request,
                was_successful=False,
                message='Authorization code missing from callback request.',
            )
        except Exception:
            logger.exception('Failed to log missing authorization code during login callback')

        return HttpResponse("Error: code not received.", status=400)

    code = request.GET['code']
    state = request.GET.get('state')

    # Validate the state parameter (if you passed one in the authorization request)

    # MSAL Config
    tenant_id = os.getenv('AZURE_TENANT_ID')
    authority_url = f'https://login.microsoftonline.com/{tenant_id}'
    client_id = os.getenv('AIT_SOC_MSAL_VICRE_CLIENT_ID')
    client_secret = os.getenv('AIT_SOC_MSAL_VICRE_MSAL_SECRET_VALUE')
    # Use configured redirect URI (supports local HTTP or production HTTPS)
    redirect_uri = settings.AZURE_AD['REDIRECT_URI']

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
        

        # Use the access token to make a request to the Microsoft Graph API
        graph_api_endpoint = 'https://graph.microsoft.com/v1.0/me/?$select=onPremisesImmutableId,userPrincipalName,givenName,surname,mail'
#       {
#           "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
#           "businessPhones": [],
#           "displayName": "Victor Reipur",
#           "givenName": "Victor",
#           "jobTitle": "IT-sikkerhedsanalytiker",
#           "mail": "vicre@dtu.dk",
#           "mobilePhone": null,
#           "officeLocation": "B:305,R:125",
#           "preferredLanguage": null,
#           "surname": "Reipur",
#           "userPrincipalName": "vicre@dtu.dk",
#           "id": "15e7b0ef-57de-4e21-a8de-c95696a736e7"
#       }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }


        
        # Make the GET request to the Graph API to get user details
        graph_response = requests.get(graph_api_endpoint, headers=headers)
        activity_username = None

        if graph_response.status_code == 200:
            # Successful request to the Graph API
            user_data = graph_response.json()


            # Extract the preferred username (which could be the user's email)
            user_principal_name = user_data.get('userPrincipalName')
            on_premises_immutable_id = user_data.get('onPremisesImmutableId')
            username = user_data.get('userPrincipalName').rsplit('@')[0] # vicre@dtu.dk
            activity_username = user_principal_name or username
            first_name = user_data.get('givenName')
            last_name = user_data.get('surname')
            email = user_data.get('mail')




            from app.scripts.azure_user_is_synced_with_on_premise_users import azure_user_is_synced_with_on_premise_users
            if not azure_user_is_synced_with_on_premise_users(sam_accountname=username, on_premises_immutable_id=on_premises_immutable_id):
                try:
                    from myview.models import UserActivityLog

                    UserActivityLog.log_login(
                        username=activity_username or username,
                        request=request,
                        was_successful=False,
                        message="Azure AD account is not synchronised with on-premises users.",
                    )
                except Exception:
                    logger.exception('Failed to log unsuccessful login due to unsynchronised Azure AD account')

                raise ValueError(f"The account you logged in with ({user_principal_name}) is not synched with on-premise users, which is a requirement.")


            from .scripts.user_have_onpremises_adm_account import user_have_onpremises_adm_account
            user_have_onpremises_adm_account = user_have_onpremises_adm_account(user_principal_name)
            if not user_have_onpremises_adm_account:
                # Construct the dynamic part of the message based on user's principal name.
                adm_account_suffix = user_principal_name.split('@')[0]
                denial_message = (
                    "You are not authenticated because the Azure user with which you have logged in does not have an on-premises admin account. "
                    f"The account adm-{adm_account_suffix}* does not appear to exist in Active Directory. This restriction is in place to allow only IT staff to access this application. "
                    "If you believe this is an error or need access, please contact vicre@dtu.dk."
                )

                try:
                    from myview.models import UserActivityLog

                    UserActivityLog.log_login(
                        username=activity_username or username,
                        request=request,
                        was_successful=False,
                        message="Login denied because no matching on-premises admin account was found.",
                    )
                except Exception:
                    logger.exception('Failed to log login denial due to missing on-premises admin account')

                return HttpResponse(denial_message, status=403)


            
            from app.scripts.create_or_update_django_user import create_or_update_django_user
            create_or_update_django_user(username=username, first_name=first_name, last_name=last_name, email=email)
            user = User.objects.get(username=username)
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            # Sync user AD groups
            from myview.models import ADGroupAssociation
            ADGroupAssociation.sync_user_ad_groups(username=user.username)

            login(request, user)
            try:
                UserLoginLog.objects.create(
                    user=user,
                    user_principal_name=user_principal_name or '',
                    ip_address=_get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    session_key=request.session.session_key or '',
                    additional_info={
                        "graph_user_id": user_data.get('id'),
                        "displayName": user_data.get('displayName'),
                    },
                )
            except Exception:
                logger = logging.getLogger(__name__)
                logger.warning("Failed to record user login event for %s", user.username, exc_info=True)

            try:
                from myview.models import UserActivityLog

                UserActivityLog.log_login(
                    user=user,
                    username=username,
                    request=request,
                    was_successful=True,
                    message="Login successful via MSAL callback.",
                )
            except Exception:
                logger.exception('Failed to log successful login for %s', username)

            if user.is_superuser:
                return HttpResponseRedirect(reverse('admin:index'))
            else:
                return redirect('/myview/frontpage/')
            
        else:
            # Handle failure or show an error message to the user
            try:
                from myview.models import UserActivityLog

                UserActivityLog.log_login(
                    username=activity_username or request.GET.get('login_hint', ''),
                    request=request,
                    was_successful=False,
                    message=f"Failed to retrieve user information from Graph API (status {graph_response.status_code}).",
                )
            except Exception:
                logger.exception('Failed to log login failure when Graph API returned status %s', graph_response.status_code)

            return HttpResponse("Error: failed to retrieve user information.", status=graph_response.status_code)
    else:
        # Handle failure or show an error message to the user
        try:
            from myview.models import UserActivityLog

            UserActivityLog.log_login(
                username=request.GET.get('login_hint', ''),
                request=request,
                was_successful=False,
                message="Failed to retrieve access token from MSAL authorization code exchange.",
            )
        except Exception:
            logger.exception('Failed to log login failure due to missing access token')

        return HttpResponse("Error: failed to retrieve access token.", status=400)


@require_GET
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def health_check(request):
    """Lightweight endpoint used for upstream health probes."""

    response = JsonResponse({"status": "ok"})
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
    





















































































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
    logger = logging.getLogger(__name__)
    start_time = time.monotonic()
    logger.info(
        "MSAL login start client_id=%s redirect_uri=%s scope=%s",
        settings.AZURE_AD['CLIENT_ID'],
        settings.AZURE_AD['REDIRECT_URI'],
        settings.AZURE_AD['SCOPE'],
    )

    try:
        client_app = ConfidentialClientApplication(
            settings.AZURE_AD['CLIENT_ID'],
            authority=settings.AZURE_AD['AUTHORITY'],
            client_credential=settings.AZURE_AD['CLIENT_SECRET'],
        )
        logger.debug("MSAL client init OK in %.1fms", (time.monotonic() - start_time) * 1000)

        # Get the URL of the Microsoft login page
        auth_started = time.monotonic()
        auth_url = client_app.get_authorization_request_url(
            scopes=settings.AZURE_AD['SCOPE'],
            redirect_uri=settings.AZURE_AD['REDIRECT_URI']
        )
        logger.info(
            "MSAL auth URL generated in %.1fms total_elapsed=%.1fms",
            (time.monotonic() - auth_started) * 1000,
            (time.monotonic() - start_time) * 1000,
        )
    except Exception:
        logger.exception("MSAL login failed")
        raise

    return redirect(auth_url)
























































def msal_logout(request):
    
    logout(request)
    # Send users to Azure logout then back to our frontpage.
    base_url = os.getenv('SERVICE_URL_WEB', 'http://localhost:8121').rstrip('/')
    post_logout_redirect = f"{base_url}/myview/frontpage/"
    logout_url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri="
        + urllib.parse.quote(post_logout_redirect, safe="")
    )
    response = redirect(logout_url)
    response.delete_cookie('csrftoken')
    return response














