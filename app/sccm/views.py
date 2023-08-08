from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer, SCCMSerializer
from sccm.scripts.sccm_get_computer_info import get_computer_info

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer



class SCCMViewSet(viewsets.ViewSet): # Note the change here
    # """
    # A viewset for retrieving SCCM computer info.
    # """

    # def create(self, request):
    #     """
    #     Retrieve SCCM computer info by computer name.

    #     Expected input:
    #     {
    #         "computer_name": "DTU-CND1363SBJ"
    #     }
    #     """
    #     computer_name = request.data.get('computer_name')
    #     if not computer_name:
    #         return Response({'error': 'Computer name required'}, status=status.HTTP_400_BAD_REQUEST)
    #     computer_info = get_computer_info(computer_name)
    #     serializer = SCCMSerializer(data=computer_info)
    #     if serializer.is_valid():
    #         return Response(serializer.data)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    """
    A viewset for retrieving SCCM computer info.
    """
    def retrieve(self, request, computer_name=None):
        """
        Retrieve SCCM computer info by computer name.

        Expected input:
        {
            "computer_name": "DTU-CND1363SBJ"
        }
        """
        computer_info = get_computer_info(computer_name)
        serializer = SCCMSerializer(data=computer_info)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        