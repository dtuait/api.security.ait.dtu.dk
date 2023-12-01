from rest_framework import viewsets, status
from rest_framework.response import Response
import json

from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from rest_framework.exceptions import ParseError
from .serializers import QuerySerializer
from .scripts.graph_apicall_runhuntingquery import run_hunting_query

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
        
        # serialize incoming data
        serializer = QuerySerializer(data=request.data)
        
        # Check if property query exists
        if serializer.is_valid():
            query = serializer.validated_data['Query']

            result = run_hunting_query(query)

            # Now you can use `query` in your code
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

