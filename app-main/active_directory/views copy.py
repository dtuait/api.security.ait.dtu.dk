from ldap3 import ALL_ATTRIBUTES
from rest_framework import viewsets, status
from rest_framework.response import Response
# from .models import Item
# from .serializers import ItemSerializer, ComputerInfoSerializer
# from sccm.scripts.sccm_get_computer_info import get_computer_info
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from .services import get_inactive_computers
from graph.views import APIAuthBaseViewSet
from rest_framework.decorators import action
from utils.active_directory_query import active_directory_query
from django.http import JsonResponse




class ActiveDirectoryQueryViewSet(APIAuthBaseViewSet):

    @swagger_auto_schema(
        method='get',
        operation_description="Query Active Directory based on given criteria.",
        manual_parameters=[
            openapi.Parameter(
                name='base_dn',
                in_=openapi.IN_QUERY,
                description="Base DN for search. Example: 'DC=win,DC=dtu,DC=dk'",
                type=openapi.TYPE_STRING,
                required=True,
                default='DC=win,DC=dtu,DC=dk'
            ),
            openapi.Parameter(
                name='search_filter',
                in_=openapi.IN_QUERY,
                description="LDAP search filter. Example: '(objectClass=user)'",
                type=openapi.TYPE_STRING,
                required=True,
                default='(objectClass=user)'
            ),
            openapi.Parameter(
                name='search_attributes',
                in_=openapi.IN_QUERY,
                description="Comma-separated list of attributes to retrieve, or 'ALL_ATTRIBUTES' to fetch all. Example: 'cn,mail'",
                type=openapi.TYPE_STRING,
                required=False,
                default='ALL_ATTRIBUTES'
            ),
            openapi.Parameter(
                name='limit',
                in_=openapi.IN_QUERY,
                description="Limit for number of results. Example: 100",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=100
            ),
        ],
        responses={200: 'Successful response with the queried data'}
    )


    @action(detail=False, methods=['get'], url_path='query')
    def query(self, request):
        # Extract query parameters
        base_dn = request.query_params.get('base_dn')
        search_filter = request.query_params.get('search_filter')
        search_attributes = request.query_params.get('search_attributes', ALL_ATTRIBUTES)
        limit = request.query_params.get('limit')

        # Convert limit to integer if present
        if limit is not None:
            limit = int(limit)

        # Convert search_attributes from comma-separated string to list if not ALL_ATTRIBUTES
        if search_attributes == 'ALL_ATTRIBUTES':
            search_attributes = ALL_ATTRIBUTES
        else:
            search_attributes = search_attributes.split(',')

        # Call the active_directory_query function
        results = active_directory_query(
            base_dn=base_dn,
            search_filter=search_filter,
            search_attributes=search_attributes,
            limit=limit
        )


        def decode_bytes(data):
            if isinstance(data, bytes):
                return data.decode('utf-8')  # or the appropriate encoding
            elif isinstance(data, dict):
                return {key: decode_bytes(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [decode_bytes(item) for item in data]
            return data

        # Decode byte strings in results before returning
        decoded_results = decode_bytes(results)
        return JsonResponse(decoded_results, safe=False)
        # # Return the results
        # return Response(results)
        # return JsonResponse(results, safe=False)







class ADComputerViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]  # Require token authentication for this view
    permission_classes = [IsAuthenticated]  # Require authenticated user for this view


    header_parameter = openapi.Parameter(
        'Authorization',  # name of the header
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Type: Token \<token\>",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True  # if the header is required or not
    )

    @swagger_auto_schema(
        manual_parameters=[header_parameter],
        operation_description="""
        Retrieve AD computers
        
        You can only query computers under this OU: <ou_variable>

        Curl example: \n
        \t curl --location 'https://api.security.ait.dtu.dk/active-directory/computer/v1-0-0/<str:computer_name>/'
        \t\t  --header 'Authorization: Token \<token\>'
        

        """,
        responses={
            # 200: ComputerInfoSerializer(),
            400: 'Error: Computer name must be provided.',
            404: 'Error: No computer found with given name',
            500: 'Error: Internal server error'
        },

    )


    def retrieve(self, request, computer_name=None):
        # Check if the computer_name is None, or is an empty string, or with only spaces
        if computer_name is None or computer_name.strip() == "":
            return Response({"error": "Computer name must be provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the computer info
        # computer_info, error = get_computer_info(computer_name)

        # if error startswith "No computer found with name"
        # if error:
        #     if error.startswith("No computer found with name"):
        #         return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
        #     elif error.startswith("Internal server error"):
        #         return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        #     else:
        #         return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # return Response(computer_info, status=status.HTTP_200_OK)
        return Response({"error": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)
    





class ADInactiveComputersViewset(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]  # Require token authentication for this view
    permission_classes = [IsAuthenticated]  # Require authenticated user for this view

    
    header_parameter = openapi.Parameter(
        'Authorization',  # name of the header
        in_=openapi.IN_HEADER,  # where the parameter is located
        description="Type: Token \<token\>",
        type=openapi.TYPE_STRING,  # type of the parameter
        required=True  # if the header is required or not
    )

    @swagger_auto_schema(
        manual_parameters=[header_parameter],
        operation_description="""
        Retrieve inactive computers
        
        You can only query computers under this OU: <ou_variable>

        Curl example: \n
        \t curl --location 'http://api.security.ait.dtu.dk/active-directory/computer/v1-0-0/inactive-computers'
        \t\t  --header 'Authorization: Token \<token\>'
        

        """,
        responses={
            # 200: ComputerInfoSerializer(),
            400: 'Error: Computer name must be provided.',
            404: 'Error: No computer found with given name',
            500: 'Error: Internal server error'
        },

    )
    
    # that endpoint retrives a list of computers that has not been logged in for x days - default 30 days
    def retrieve(self, request):

        # get the query params
        days = request.query_params.get('days', 30)

        ou = request.query_params.get('ou', 'DC=win,DC=dtu,DC=dk')
        
        # Get the soon disabled computers
        inactive_computers = get_inactive_computers(days, ou)

        return Response(inactive_computers, status=status.HTTP_200_OK)

        # 
        
        # return Response({"error": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
