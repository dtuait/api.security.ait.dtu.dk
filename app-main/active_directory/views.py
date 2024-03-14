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
    
