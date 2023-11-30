from rest_framework import viewsets, status
from rest_framework.response import Response
import json
from sccm.scripts.sccm_get_computer_info import get_computer_info
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from rest_framework.exceptions import ParseError
from .serializers import QuerySerializer

from rest_framework.decorators import action

class GraphHuntingViewSet(viewsets.ViewSet):

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


    @action(detail=False, methods=['post'], url_path='runHuntingQuery')


    def run_hunting_query(self, request):
        serializer = QuerySerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['Query']

            # Now you can use `query` in your code
            return Response({'Query': query}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class GraphHuntingViewSet(viewsets.ViewSet):


#     authentication_classes = [TokenAuthentication]  # Require token authentication for this view
#     permission_classes = [IsAuthenticated]  # Require authenticated user for this view


#     header_parameter = openapi.Parameter(
#         'Authorization',  # name of the header
#         in_=openapi.IN_HEADER,  # where the parameter is located
#         description="Type: Token \<token\>",
#         type=openapi.TYPE_STRING,  # type of the parameter
#         required=True  # if the header is required or not
#     )

#     @swagger_auto_schema(
#         manual_parameters=[header_parameter],
#         operation_description="""
#         Hunting query description
#         """,
#         responses={
#             200: 'ComputerInfoSerializer()',
#             400: 'Error: 1',
#             404: 'Error: 2',
#             500: 'Error: Internal server error'
#         },

#     )



#     def retrieve(self, request, pk=None):

#         return Response({'message': 'Hello, World!'}, status=status.HTTP_200_OK)
 