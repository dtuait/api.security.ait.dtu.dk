from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
import json

from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from rest_framework.exceptions import ParseError
from .serializers import QuerySerializer
# from .scripts.graph_apicall_runhuntingquery import run_hunting_query
from .services import execute_hunting_query, execute_get_user, execute_list_user_authentication_methods

from rest_framework.decorators import action



class HuntingQueryViewSet(viewsets.ViewSet):

    authentication_classes = [TokenAuthentication]  # Require token authentication for this view
    permission_classes = [IsAuthenticated]  # Require authenticated user for this view


    autho_bearer_token = openapi.Parameter(
        'Authorization',  # name of the header
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Required. Must be in the format 'Token \<token\>'.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True  # if the header is required or not
    )

    content_type_parameter = openapi.Parameter(
        'Content-Type',  # name of the header
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Required. Must be 'application/json'.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True  # if the header is required or not
    )

    @swagger_auto_schema(
        manual_parameters=[autho_bearer_token, content_type_parameter],
        operation_description="""
        Hunting query description
        """,
        responses={
            200: 'ComputerInfoSerializer()',
            400: 'Error: 1',
            404: 'Error: 2',
            500: 'Error: Internal server error'
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['Query'],
            properties={
                'Query': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example='<kql query>'
                )
            },
        ),
    )


    @action(detail=False, methods=['post'], url_path='run-hunting-query')


    def run_hunting_query(self, request):
        try:
            # serialize incoming data
            serializer = QuerySerializer(data=request.data)

            # Raise an exception if the data is not valid
            serializer.is_valid(raise_exception=True)

            # Extract the validated query
            query = serializer.validated_data['Query']

            # Execute the hunting query
            response, status_code = execute_hunting_query(query)

            # Return the response
            return Response(response, status=status_code)
        
        except ValidationError as e:
            # Handle validation errors from the serializer
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle other unforeseen exceptions
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






















class GetUserViewSet(viewsets.ViewSet):


    authentication_classes = [TokenAuthentication]  # Require token authentication for this view
    permission_classes = [IsAuthenticated]  # Require authenticated user for this view


    autho_bearer_token = openapi.Parameter(
        'Authorization',  # name of the header        
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Required. Must be in the format 'Token \<token\>'.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the header is required or not
        default='Token <token>'  # default value
    )

    user_path_param = openapi.Parameter(
        'user',  # name of the path parameter
        in_=openapi.IN_PATH,  # location of the parameter
        description="The username requested for retrieval",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the path parameter is required
        default='vicre-test01@dtudk.onmicrosoft.com',  # default value
        override=True  # override the default value
    )

    @swagger_auto_schema(
        manual_parameters=[autho_bearer_token, user_path_param],
        operation_description="""
        Get the user info for the given username.

        Curl example: \n
        \t curl --location --request GET 'https://api.security.ait.dtu.dk/v1.0/graph/get-user/<user>'
        \t\t  --header 'Authorization: Token \<token\>'



        Response example:
        ```json
        {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
            "businessPhones": [],
            "displayName": "vicre-test01",
            "givenName": "Victors test bruger",
            "jobTitle": "test bruger",
            "mail": "vicre-test01@dtudk.onmicrosoft.com",
            "mobilePhone": null,
            "officeLocation": null,
            "preferredLanguage": null,
            "surname": null,
            "userPrincipalName": "vicre-test01@dtudk.onmicrosoft.com",
            "id": "3358461b-2b36-4019-a2b7-2da92001cf7c"
        }
        ```
        """,
        responses={
            200: 'Successfully got user',
            400: 'Error: 1',
            404: 'Error: 2',
            500: 'Error: Internal server error'
        },
  
    )


    @action(detail=False, methods=['get'], url_path='get_user')


    def get_user(self, request, user):
            

        response, status_code = execute_get_user(user)

        return Response(response, status=status_code)




        # return Response({'error': 'Not implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)





















class ListUserAuthenticationMethodsViewSet(viewsets.ViewSet):




    authentication_classes = [TokenAuthentication]  # Require token authentication for this view
    permission_classes = [IsAuthenticated]  # Require authenticated user for this view


    autho_bearer_token = openapi.Parameter(
        'Authorization',  # name of the header        
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Required. Must be in the format 'Token \<token\>'.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the header is required or not
        default='Token <token>'  # default value
    )

    user_path_param = openapi.Parameter(
        'user_id__or__user_principalname',  # name of the path parameter
        in_=openapi.IN_PATH,  # location of the parameter
        description="Get user authentication methods for the given user id",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the path parameter is required
        default='vicre-test01@dtudk.onmicrosoft.com',  # default value
        override=True  # override the default value
    )

    @swagger_auto_schema(
        manual_parameters=[autho_bearer_token, user_path_param],
        operation_description="""
        Get the user authentication methods for the given user id.

        Microsoft Graph API documentation: https://learn.microsoft.com/en-us/graph/api/microsoftauthenticatorauthenticationmethod-list?view=graph-rest-1.0&tabs=http
        
        Response example using sms as mfa method:
        ```
        {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('vicre-test01%40dtudk.onmicrosoft.com')/authentication/methods",
            "value": [
                {
                "@odata.type": "#microsoft.graph.phoneAuthenticationMethod",
                "id": "3179e48a-750b-4051-897c-87b9720928f7",
                "phoneNumber": "+45 24213819",
                "phoneType": "mobile",
                "smsSignInState": "notAllowedByPolicy"
                },
                {
                "@odata.type": "#microsoft.graph.passwordAuthenticationMethod",
                "id": "28c10230-6103-485e-b985-444c60001490",
                "password": null,
                "createdDateTime": "2024-03-12T13:25:21Z"
                }
            ]
        }
        ```

        """,
        responses={
            200: 'Successfully got user methods',
            400: 'Error: 1',
            404: 'Error: 2',
            500: 'Error: Internal server error'
        },
  
    )


    @action(detail=False, methods=['get'], url_path='list_user_authentication_methods')


    def list_user_authentication_methods(self, request, user_id__or__user_principalname):

        response, status_code = execute_list_user_authentication_methods(user_id__or__user_principalname)

        return Response(response, status=status_code)

        # return Response({'error': 'Not implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)





































class DeleteMfaViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]  # Require token authentication for this view
    permission_classes = [IsAuthenticated]  # Require authenticated user for this view


    autho_bearer_token = openapi.Parameter(
        'Authorization',  # name of the header        
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Required. Must be in the format 'Token \<token\>'.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the header is required or not
        default='Token <token>'  # default value
    )

    user_path_param = openapi.Parameter(
        'user',  # name of the path parameter
        in_=openapi.IN_PATH,  # location of the parameter
        description="The username for which the MFA solution will be deleted",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the path parameter is required
        default='vicre-test01@dtudk.onmicrosoft.com',  # default value
        override=True  # override the default value
    )

    @swagger_auto_schema(
        manual_parameters=[autho_bearer_token, user_path_param],
        operation_description="""
        Incoming user MFA solutions will be deleted, thereby giving users space to re-enable MFA by deleting their MFA solution on the app, then visiting office.com and signing in with <user>@dtu.dk to re-enable MFA.

        Microsoft Graph API documentation: https://learn.microsoft.com/en-us/graph/api/microsoftauthenticatorauthenticationmethod-delete?view=graph-rest-1.0&tabs=http

        Curl example: \n
        \t curl --location --request DELETE 'https://api.security.ait.dtu.dk/graph/security/delete-mfa/<user>'
        \t\t  --header 'Authorization: Token \<token\>'
        """,
        responses={
            204: 'Successfully deleted MFA', # No content - meaning the request was successful
            400: 'Error: 1',
            404: 'Error: 2',
            500: 'Error: Internal server error'
        },
  
    )


    @action(detail=False, methods=['delete'], url_path='delete-mfa')


    def delete_mfa(self, request, user):

        




        return Response({'error': 'Not implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)















class UnlockMfaViewSet(viewsets.ViewSet):
    pass


