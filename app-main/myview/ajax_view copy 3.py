
from .views import BaseView
from django.http import JsonResponse
from .models import ADGroupAssociation
from django.contrib.auth.models import User
from active_directory.scripts.active_directory_query import active_directory_query
from ldap3 import ALL_ATTRIBUTES
import json
import logging

# Get the logger for your app
logger = logging.getLogger(__name__)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class AjaxView(BaseView):

    # Ensure CSRF exemption and login required
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AjaxView, self).dispatch(request, *args, **kwargs)

    def create_custom_token(self, request):
        user = User.objects.get(username=request.user.username)
        # Generate random string of length 255
        token = user.generate_new_custom_token()
        return JsonResponse({'custom_token': token.key})

    # Chat-related methods
    def create_chat_thread(self, request):
        user = request.user
        from .models import ChatThread
        thread = ChatThread.objects.create(user=user)
        return JsonResponse({'thread_id': thread.id, 'title': thread.title})

    def get_chat_threads(self, request):
        user = request.user
        from .models import ChatThread
        threads = ChatThread.objects.filter(user=user).order_by('-created_at')
        thread_list = [{'id': t.id, 'title': t.title} for t in threads]
        return JsonResponse({'threads': thread_list})

    def send_message(self, request):
        user = request.user
        thread_id = request.POST.get('thread_id')
        message_content = request.POST.get('message')

        if not thread_id or not message_content:
            return JsonResponse({'error': 'Thread ID and message content are required'}, status=400)

        try:
            from .models import ChatThread, ChatMessage
            thread = ChatThread.objects.get(id=thread_id, user=user)
        except ChatThread.DoesNotExist:
            return JsonResponse({'error': 'Chat thread not found'}, status=404)

        # Save user's message
        user_message = ChatMessage.objects.create(
            thread=thread,
            role='user',
            content=message_content
        )

        # Retrieve previous messages to build context
        messages = ChatMessage.objects.filter(thread=thread).order_by('timestamp')
        context = [{'role': msg.role, 'content': msg.content} for msg in messages]

        # Call the assistant function
        from active_directory.services import active_directory_query_assistant

        try:
            # Call the assistant function with context
            response_data, updated_context = active_directory_query_assistant(
                user_prompt=message_content,
                context=context[:-1]  # Exclude the latest user message (it's already included in user_prompt)
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        # Save assistant's response
        assistant_message = ChatMessage.objects.create(
            thread=thread,
            role='assistant',
            content=json.dumps(response_data)  # Store JSON as string
        )

        return JsonResponse({'assistant_response': response_data})

    def get_chat_messages(self, request):
        user = request.user
        thread_id = request.POST.get('thread_id')

        if not thread_id:
            return JsonResponse({'error': 'Thread ID is required'}, status=400)

        try:
            from .models import ChatThread, ChatMessage
            thread = ChatThread.objects.get(id=thread_id, user=user)
        except ChatThread.DoesNotExist:
            return JsonResponse({'error': 'Chat thread not found'}, status=404)

        messages = ChatMessage.objects.filter(thread=thread).order_by('timestamp')
        message_list = [{
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        } for msg in messages]

        return JsonResponse({'messages': message_list})

    def post(self, request, *args, **kwargs):
        logger.info("Received POST request at /myview/ajax/")
        logger.info("Request method: %s", request.method)
        logger.info("Request headers: %s", request.headers)
        logger.info("Request Content-Type: %s", request.META.get('CONTENT_TYPE'))
        logger.info("Request POST data: %s", request.POST)
        logger.info("Request user: %s", request.user.username if request.user.is_authenticated else "Anonymous")
        logger.info("CSRF Token in META: %s", request.META.get('CSRF_COOKIE'))
        logger.info("CSRF Token in POST: %s", request.POST.get('csrfmiddlewaretoken'))

        # Avoid decoding binary data
        if 'multipart/form-data' not in request.content_type:
            try:
                logger.info("Raw Request Body: %s", request.body.decode('utf-8'))
            except UnicodeDecodeError as e:
                logger.error("Error decoding request body: %s", e)
        else:
            logger.info("Multipart/form-data detected; skipping raw body logging.")

        action = request.POST.get('action')

        if action is None:
            logger.error("No action specified in the POST data.")
            return JsonResponse({'error': 'No action provided'}, status=400)

        try:
            print("action: ", action)

            if action == 'create_chat_thread':
                return self.create_chat_thread(request)
            elif action == 'get_chat_threads':
                return self.get_chat_threads(request)
            elif action == 'send_message':
                return self.send_message(request)
            elif action == 'get_chat_messages':
                return self.get_chat_messages(request)

            # Existing actions
            elif action == 'clear_my_ad_group_cached_data':
                from django.core.cache import cache
                try:
                    cache.clear()
                    return JsonResponse({'success': 'Cache cleared'})
                except Exception as e:
                    return JsonResponse({'error': str(e)})

            elif action == 'create_custom_token':
                if request.user.is_authenticated:
                    return self.create_custom_token(request)
                

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


        except Exception as e:
            logger.error(f"Error processing action '{action}': {e}")
            return JsonResponse({'error': str(e)}, status=500)
