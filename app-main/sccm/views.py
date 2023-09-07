from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer, SCCMSerializer
from sccm.scripts.sccm_get_computer_info import get_computer_info
from drf_yasg.utils import swagger_auto_schema




class SCCMViewSet(viewsets.ViewSet): # Note the change here

    
    @swagger_auto_schema(
        operation_description="""
        Retrieve computer information by name.
        
        You can only query computers under this OU: <ou_variable>

        Expected input:
        {
            "computer_name": "DTU-CND1363SBJ"
        }
        """,
        responses={
            200: SCCMSerializer(),
            400: 'Error: Computer name must be provided.',
            404: 'Error: No computer found with given name',
            500: 'Error: Internal server error'
        },
    )

    # """
    # A viewset for retrieving SCCM computer info.
    # """
    def retrieve(self, request, computer_name=None):

        # Check if the computer_name is None, or is an empty string, or with only spaces
        if computer_name is None or computer_name.strip() == "":
            return Response({"error": "Computer name must be provided."}, status=status.HTTP_400_BAD_REQUEST)
        

        # Get the computer info
        computer_info, error = get_computer_info(computer_name)

        # if error startswith "No computer found with name"
        if error:
            if error.startswith("No computer found with name"):
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
            elif error.startswith("Internal server error"):
                return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = SCCMSerializer(computer_info)
        return Response(serializer.data)
