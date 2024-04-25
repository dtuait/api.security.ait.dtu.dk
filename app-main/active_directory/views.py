from ldap3 import ALL_ATTRIBUTES
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from .services import get_inactive_computers
from graph.views import APIAuthBaseViewSet
from rest_framework.decorators import action
from .services import execute_active_directory_query











class ActiveDirectoryQueryViewSet(APIAuthBaseViewSet):

    @swagger_auto_schema(
        method='get',
        operation_description="""Query Active Directory based on given criteria. This endpoint allows querying for
        Active Directory objects with flexibility in specifying which attributes to return, applying filters, and
        pagination control. The synergy between the parameters allows for tailored queries. For instance, 'base_dn'
        specifies the starting point within the AD structure. 'search_filter' narrows down the objects based on
        specified conditions. 'search_attributes' controls which attributes of the objects are retrieved, and 'limit'
        provides pagination capability. 'excluded_attributes' can further refine the returned data by excluding
        specified attributes from the response, enhancing query efficiency and relevance.
        
        
        Get infomation about a specific user, based on initial
        (sAMAccountName=vicre)

        
        """,
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
            openapi.Parameter(
                name='excluded_attributes',
                in_=openapi.IN_QUERY,
                description="Comma-separated list of attributes to exclude from the results. Default is 'thumbnailPhoto'. Example: 'thumbnailPhoto,someOtherAttribute'",
                type=openapi.TYPE_STRING,
                required=False,
                default='thumbnailPhoto'
            ),
        ],
        responses={200: 'Successful response with the queried data'}
    )

    @action(detail=False, methods=['get'], url_path='query')
    def query(self, request):
        base_dn = request.query_params.get('base_dn')
        search_filter = request.query_params.get('search_filter')
        search_attributes = request.query_params.get('search_attributes', ALL_ATTRIBUTES)
        limit = request.query_params.get('limit', None)
        excluded_attributes = request.query_params.get('excluded_attributes', 'thumbnailPhoto').split(',')

        if limit is not None:
            limit = int(limit)

        if search_attributes == 'ALL_ATTRIBUTES' or search_attributes is '*' or search_attributes == None:
            search_attributes = ALL_ATTRIBUTES
        else:
            search_attributes = search_attributes.split(',')

        results = execute_active_directory_query(
            base_dn=base_dn,
            search_filter=search_filter,
            search_attributes=search_attributes,
            limit=limit,
            excluded_attributes=excluded_attributes
        )

        return Response(results)




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
    
