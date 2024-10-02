
from .views import BaseView
from django.http import JsonResponse
from .models import ADGroupAssociation
from django.contrib.auth.models import User
from active_directory.scripts.active_directory_query import active_directory_query
from ldap3 import ALL_ATTRIBUTES
import json


class AjaxView(BaseView):

    def post(self, request, *args, **kwargs):
        # Extract an 'action' parameter from the POST request to determine which method to call
        action = request.POST.get('action')


















        if action == 'clear_my_ad_group_cached_data':
            from django.core.cache import cache
            try:
                
                cache.clear()
                return JsonResponse({'success': 'Cache cleared'})
            except Exception as e:
                return JsonResponse({'error': str(e)})





































        elif action == 'create_custom_token':
            if request.user.is_authenticated:
                return self.create_custom_token(request)
            



























        elif action == 'copilot-chatgpt-basic':
            if request.user.is_authenticated:
                # return not implemented yet status 200
                content = request.POST.get('content')
                user = json.loads(content)

                from chatgpt_app.scripts.openai_basic import get_openai_completion

                message = get_openai_completion(
                    system="You return 1 ldap3 query at a time. Give me a ldap3 query that returns user name vicre >> (sAMAccountName=vicre). Do not explain the query, just provide it.",
                    user=user['user']
                )

                return JsonResponse({'message': message.content})


        elif action == 'copilot-active-directory-query':
            if request.user.is_authenticated:
                content = request.POST.get('content')
                user_input = json.loads(content)
                user_query = user_input.get('user')

                from chatgpt_app.scripts.active_directory_assistant import run_assistant_query

                # Run the assistant to get the query parameters and result
                try:
                    query_result = run_assistant_query(user_query)

                    # Return the result
                    return JsonResponse(query_result, safe=False)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)







































        elif action == 'active_directory_query':
            # Extract the parameters from the POST request
            base_dn = request.POST.get('base_dn')
            search_filter = request.POST.get('search_filter')
            search_attributes = request.POST.get('search_attributes')
            search_attributes = search_attributes.split(',') if search_attributes else ALL_ATTRIBUTES
            limit = request.POST.get('limit')
            
            if limit is not None:
                limit = int(limit)


            # Perform the active directory query
            result = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=limit)
            # return Response(result)
            return JsonResponse(result, safe=False)
        

        






































        elif action == 'ajax_change_form_update_form_ad_groups':
            # Extract ad_groups = [] from the POST request
            ad_groups = request.POST.getlist('ad_groups')
            # convert ad_groups[0] into a list. The data is JSON encoded in the POST request
            ad_groups = json.loads(ad_groups[0])

            request.session['ajax_change_form_update_form_ad_groups'] = ad_groups

            # logger.info(f"Session data after setting ad_groups: {request.session.items()}")
            request.session.save()

            # reload the page
            # return redirect(path) # '/admin/myview/endpoint/1/change/'


            return JsonResponse({'success': 'Form updated'})








































        elif action == 'ajax__search_form__add_new_organizational_unit':
            
            try:
                # Extract the parameters from the POST request
                base_dn = 'DC=win,DC=dtu,DC=dk'
                distinguished_name = request.POST.get('distinguished_name')
                search_filter = f'(&(objectClass=organizationalUnit)(distinguishedName={distinguished_name}))'
                search_attributes = 'distinguishedName,canonicalName'.split(',')
                limit = 1

                if limit is not None:
                    limit = int(limit)

                # Perform the active directory query
                organizational_unit = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=limit)

                # If len(organizational_unit) != 1 then return error JsonResponse
                if len(organizational_unit) != 1:
                    raise ValueError("No match found for the distinguished name.")

                # Get or create a new ADOrganizationalUnitLimiter
                from .models import ADOrganizationalUnitLimiter
                ou_limiter, created = ADOrganizationalUnitLimiter.objects.get_or_create(
                    canonical_name=organizational_unit[0]['canonicalName'][0],
                    distinguished_name=organizational_unit[0]['distinguishedName'][0]
                )

                if created:
                    return JsonResponse({'success': 'New organizational unit created'}, status=201)
                else:
                    return JsonResponse({'success': 'Organizational unit already exists'}, status=200)


            except Exception as e:
                from django.conf import settings
                if settings.DEBUG:
                    return JsonResponse({'error': str(e)}, status=500)
                else:
                    return JsonResponse({'error': 'Could not find organizational unit'}, status=500)












































        elif action == 'ajax__search_form__add_new_ad_group_associations':      
            try:  
                # Extract the parameters from the POST request
                base_dn = 'DC=win,DC=dtu,DC=dk'
                distinguished_name = request.POST.get('distinguished_name')
                search_filter = f'(&(objectClass=group)(distinguishedName={distinguished_name}))'
                search_attributes = 'distinguishedName,canonicalName'.split(',')
                limit = 1

                if limit is not None:
                    limit = int(limit)

                # Perform the active directory query
                organizational_unit = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=limit)

                # If len(organizational_unit) != 1 then return error JsonResponse
                if len(organizational_unit) != 1:
                    raise ValueError(f"No match found for the distinguished name:\n{distinguished_name}")

                # Get or create a new ADOrganizationalUnitLimiter
                from .models import ADGroupAssociation
                ad_group_assoc, created = ADGroupAssociation.objects.get_or_create(
                    canonical_name=organizational_unit[0]['canonicalName'][0],
                    distinguished_name=organizational_unit[0]['distinguishedName'][0]
                )


                # sync the created groups adusers members
                ADGroupAssociation.sync_ad_group_members(ad_group_assoc)

                if created:
                    return JsonResponse({'success': 'New organizational unit created'}, status=201)
                else:
                    return JsonResponse({'success': 'Organizational unit already exists'}, status=200)


            except Exception as e:
                from django.conf import settings
                if settings.DEBUG:
                    return JsonResponse({'error': str(e)}, status=500)
                else:
                    return JsonResponse({'error': 'Could not find group'}, status=500)


    










































        elif action == 'ajax_change_form_update_form_ad_ous':
            # Extract ad_ous from the POST request
            ad_ous = request.POST.getlist('ad_ous')
            # convert ad_ous[0] into a list. The data is JSON encoded in the POST request
            ad_ous = json.loads(ad_ous[0])

            request.session['ajax_change_form_update_form_ad_ous'] = ad_ous

            request.session.save()

            return JsonResponse({'success': 'Form updated'})

            
        else:
            return JsonResponse({'error': 'Invalid AJAX action'}, status=400)



    def sync_ad_groups(self, request):
        # Your logic here
        result = ADGroupAssociation.sync_ad_groups(None)
        
        return JsonResponse({'success': result})


    def create_custom_token(self, request):
        user = User.objects.get(username=request.user.username)
        # Generate random string of length 255        
        token = user.generate_new_custom_token()        
        return JsonResponse({'custom_token': token.key})






