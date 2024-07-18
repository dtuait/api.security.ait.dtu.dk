from django.forms import ValidationError
from django.http import JsonResponse
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
from rest_framework.authentication import SessionAuthentication, TokenAuthentication










class APIAuthBaseViewSet(viewsets.ViewSet):
    # The 'authentication_classes' attribute is crucial for securing our API. It determines how incoming requests should be authenticated.
    # In this case, we're using two authentication methods: SessionAuthentication and TokenAuthentication.
    # SessionAuthentication is used for users who are authenticated via a web form and have an active session.
    # TokenAuthentication is used for programmatic access to the API, where the client sends a token as part of the request.
    # The order of the classes in the list matters. Django REST Framework will use the first class that successfully authenticates.
    # This setup allows us to support both interactive browser-based usage of the API (via sessions) and programmatic usage (via tokens).
    authentication_classes = [SessionAuthentication, TokenAuthentication]





class GetUserViewSet(APIAuthBaseViewSet):

    

    autho_bearer_token = openapi.Parameter(
        'Authorization',  # name of the header        
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Required. Must be in the format '\<token\> or real token'.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the header is required or not
        default='<token>'  # default value
    )





    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'Authorization',  # name of the header        
                in_=openapi.IN_HEADER,  # where the parameter is located
                description="Required. Must be in the format '\<token\> or real token'.",
                type=openapi.TYPE_STRING,  # type of the parameter
                required=True,  # if the header is required or not
                default='<token>'  # default value
            ), 
            openapi.Parameter(
                'user',  # name of the path parameter
                in_=openapi.IN_PATH,  # location of the parameter
                description="The username requested for retrieval",
                type=openapi.TYPE_STRING,  # type of the parameter
                required=True,  # if the path parameter is required
                default='vicre-test01@dtudk.onmicrosoft.com',  # default value
                override=True  # override the default value
            ),
            openapi.Parameter(
            '$select',  # name of the query parameter
            in_=openapi.IN_QUERY,  # location of the parameter
            description="Optional. Specifies a subset of properties to include in the response.",
            type=openapi.TYPE_STRING,
            required=False
            ),
        ],


        operation_description="""
        Get the user info for the given username.

        Microsoft Graph API documentation: https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http

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
            
        select_param = request.GET.get('$select', None)

        response, status_code = execute_get_user(user, select_param)

        return Response(response, status=status_code)




        # return Response({'error': 'Not implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)





















class ListUserAuthenticationMethodsViewSet(APIAuthBaseViewSet):




    autho_bearer_token = openapi.Parameter(
        'Authorization',  # name of the header        
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Required. Must be in the format '\<token\> or real token'.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the header is required or not
        default='<token>'  # default value
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
        Curl\n
        ```
        curl -X 'GET'
        \t'http://localhost:6081/v1.0/graph/list/vicre-test01%40dtudk.onmicrosoft.com/authentication-methods'
        \t-H 'accept: application/json'
        \t-H 'Authorization: <token>'
        \t-H 'X-CSRFToken: qfp3Ahr3MGnV0aERFcjdAjkCNPVp39m77Y3d72WuUUanpJzJrcXN9TIe86t5yFL2'
        ```
        Request URL\n
        ```
        http://localhost:6081/v1.0/graph/list/vicre-test01%40dtudk.onmicrosoft.com/authentication-methods`
        ```
        Reponse\n
        ```
        {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('vicre-test01%40dtudk.onmicrosoft.com')/authentication/methods",
        "value": [
            {
            "@odata.type": "#microsoft.graph.passwordAuthenticationMethod",
            "id": "28c10230-6103-485e-b985-444c60001490",
            "password": null,
            "createdDateTime": "2024-03-12T13:25:21Z"
            },
            {
            "@odata.type": "#microsoft.graph.microsoftAuthenticatorAuthenticationMethod",
            "id": "123e4441-eadf-4950-883d-fea123988824",
            "displayName": "iPhone 12",
            "deviceTag": "SoftwareTokenActivated",
            "phoneAppVersion": "6.8.3",
            "createdDateTime": null
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





































class DeleteMfaViewSet(APIAuthBaseViewSet):


    autho_bearer_token = openapi.Parameter(
        'Authorization',  # name of the header        
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Required. Must be in the format '\<token\> or real token'.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the header is required or not
        default='<token>'  # default value
    )

    user_path_param = openapi.Parameter(
        'user_id__or__user_principalname',  # name of the path parameter
        in_=openapi.IN_PATH,  # location of the parameter
        description="The username requested for deletion of MFA.",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the path parameter is required
        default='vicre-test01@dtudk.onmicrosoft.com',  # default value
        override=True  # override the default value
    )

    microsoft_authentication_method_id = openapi.Parameter(
        'microsoft_authenticator_method_id',  # name of the path parameter
        in_=openapi.IN_PATH,  # location of the parameter
        description="The authentication method id for the MFA solution to be deleted",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True,  # if the path parameter is required
        default=None,  # default value
        override=True  # override the default value
    )

    @swagger_auto_schema(
        manual_parameters=[autho_bearer_token, user_path_param, microsoft_authentication_method_id],
        operation_description="""
        Incoming user MFA solutions will be deleted, thereby giving users space to re-enable MFA by deleting their MFA solution on the app, then visiting office.com and signing in with <user>@dtu.dk to re-enable MFA.

        Microsoft Graph API documentation: https://learn.microsoft.com/en-us/graph/api/microsoftauthenticatorauthenticationmethod-delete?view=graph-rest-1.0&tabs=http

        How the call looks when calling microsoft api: https://graph.microsoft.com/v1.0/users/{azure_user_principal_id}/authentication/microsoftAuthenticatorMethods/{authentication_method_id}

        

        Curl:
        ```
        curl -X 'DELETE'
            \t'http://localhost:6081/v1.0/graph/users/vicre-test01%40dtudk.onmicrosoft.com/authentication-methods/171397f2-804e-4664-8ede-c4b3adf6bbb0'
            \t-H 'accept: application/json'
            \t-H 'Authorization: <token>'
            \t-H 'X-CSRFToken: zVFVMDNniqLL9sdWjjcsvYrOb4haiVgfgEj5joiOqEydy18O5jQ24yPqwlPQNrFa'
        ```
        Request URL
        ```
        http://localhost:6081/v1.0/graph/users/vicre-test01%40dtudk.onmicrosoft.com/authentication-methods/171397f2-804e-4664-8ede-c4b3adf6bbb0
        ```
        Response is 204 No content. This means that the request was successful and the MFA was deleted.       



        """,
        responses={
            204: 'Successfully deleted MFA', # No content - meaning the request was successful
            400: 'Error: 1',
            404: 'Error: 2',
            500: 'Error: Internal server error'
        },
  
    )


    @action(detail=False, methods=['delete'], url_path='delete-mfa')


    def delete_mfa(self, request, user_id__or__user_principalname, microsoft_authenticator_method_id):
        from .services import execute_delete_user_authentication_method as delete_authentication_method

        try:
            response, status_code = delete_authentication_method(user_id__or__user_principalname, microsoft_authenticator_method_id)


            return Response(response, status=status_code)



            

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Failed to delete authentication method.'}, status=403)
            # return Response({'status': 'error', 'message': 'You do not have permission to delete methods on this user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
















class UnlockMfaViewSet(viewsets.ViewSet):
    pass











































class HuntingQueryViewSet(APIAuthBaseViewSet):


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



