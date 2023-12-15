from rest_framework import viewsets
from rest_framework.response import Response
from datetime import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from azure.services import execute_hunting_query



class MyMFARejectedByUser(viewsets.ViewSet):

    # require authentication
    authentication_classes = [TokenAuthentication]  # Require token authentication for this view
    permission_classes = [IsAuthenticated]  # Require authenticated user for this view

    def get_email(self, request, *args, **kwargs):
            
            try:

                # get the json data from body.
                data = request.data

                # Try to extract Query property
                query = data['object']['properties']['alerts'][0]['properties']['additionalData']['Query']

                # hunting query result
                hunting_query_result, status_code = execute_hunting_query(query)

                # email = hunting_query_result['results'][0]['UserPrincipalName']
                email = 'vicre@byg.dtu.dk'



                return Response(email, status=status_code)
            except KeyError:
                return Response({'error': 'Failed to complete'})

    def render_html(self, request, *args, **kwargs):


        try:
            # check if parameter is true
            # If it is, it meanins that instead of returning a JSON, then just return the raw value. {'my_value':'value'} -> 'value'
            to_scalar = request.query_params.get('toscalar', 'false')

            # get the json data from body.
            data = request.data
            
            # Try to extract Query property
            query = data['object']['properties']['alerts'][0]['properties']['additionalData']['Query']

            # hunting query result
            hunting_query_result, status_code = execute_hunting_query(query)


            html_body = self._gerenate_html(hunting_query_result)

       
            return Response(html_body, status=status_code)
        except KeyError:
            return Response({'error': 'Failed to extract Query property. Check the JSON structure.'})

    






    
    def _gerenate_html(self, hunting_query):

        data = hunting_query


        app_display_name = data['results'][0]['AppDisplayName']
        city = data['results'][0]['City']
        country_or_region = data['results'][0]['CountryOrRegion']
        fullname = data['results'][0]['Fullname']
        ip_address = data['results'][0]['IPAddress']
        state = data['results'][0]['State']
        time_generated = data['results'][0]['TimeGenerated'] # '2023-12-07T14:03:38.0418848Z' -> '%Y-%m-%dT%H:%M:%S.%fZ'
        # Truncate the last digit from the seconds fraction
        time_generated = time_generated[:-2] + 'Z'
        time_generated_datetime = datetime.strptime(time_generated, '%Y-%m-%dT%H:%M:%S.%fZ')
        user_pricipal_name = data['results'][0]['UserPrincipalName']




        mail_string = f"""
        Dear {fullname},
        <br>\n
        <br>\n
        This is an automated security notification. A declined Multi-Factor Authentication (MFA) request associated with your account has been recorded:
        <br>\n
        <br>\n
        <strong>Time and Date</strong>: {time_generated_datetime}
        <br>\n
        <strong>Application</strong>: {app_display_name}
        <br>\n
        <strong>User ID</strong>: {user_pricipal_name}
        <br>\n
        <strong>IP Address</strong>: {ip_address}
        <br>\n
        <strong>Location</strong>: {city}, {state}, {country_or_region}
        <br>\n
        <br>\n
        <strong>Action Required</strong>:
        <br>\n
        If you recognize this event, no further action is needed.
        <br>\n
        If you do not recognize this event, please change your password at <a href="https://password.dtu.dk/admin/change_password.aspx">password.dtu.dk</a> for security reasons.
        <br>\n
        For any concerns, contact our support team.
        <br>\n
        <br>\n
        AITSOC
        """


        return mail_string



