

def convert_guid_to_base64(guid_str):
    import base64
    # Convert the string into bytes, assuming it's stored in escaped unicode form
    bytes_guid = bytes(guid_str, 'raw_unicode_escape')
    # Encode these bytes into a Base64 string
    base64_guid = base64.b64encode(bytes_guid)
    return base64_guid.decode('utf-8')

def convert_to_base64(byte_data):
    import base64
    return base64.b64encode(byte_data).decode('utf-8')

def validate_user(user_principal_name: str, on_premises_immutable_id: str):
    from active_directory.services import execute_active_directory_query
    base_dn = "DC=win,DC=dtu,DC=dk"
    search_filter = f"(userPrincipalName={user_principal_name})"
    search_attributes = ['mS-DS-ConsistencyGuid','userPrincipalName']
    active_directory_response = execute_active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

    ms_ds_consistency_guid = convert_to_base64(active_directory_response[0]['mS-DS-ConsistencyGuid'][0])
    ad_user_principal_name = active_directory_response[0]['userPrincipalName'][0]
    
    is_synced = (ms_ds_consistency_guid == on_premises_immutable_id) # Compare the two base64 strings

    if not is_synced:
        return False
    else:
        return True
    
        username = user_principal_name.split('@')[0]
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username=username)
        # Specify the backend explicitly
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        # Now log the user in
        from django.contrib.auth import login

        return login(request, user)

    print(f'Is the user synced? {is_synced}') # >> Is the user synced? False


def run():
    from graph.services import execute_get_user
    from django.http import JsonResponse

    # This part is equal to when the user has authenticated via msal
    select_param = '$select=onPremisesImmutableId,userPrincipalName'
    user = 'adm-vicre@dtudk.onmicrosoft.com'
    response, status_code = execute_get_user(user, select_param)
    user_principal_name = response['userPrincipalName']
    on_premises_immutable_id = response.get('onPremisesImmutableId')



    is_synced = validate_user(user_principal_name=user_principal_name, on_premises_immutable_id=on_premises_immutable_id)

    if is_synced:
        print('User is authenticated')
    else:
        print('User is not authenticated')



    # if django_user is not None:
    #     return JsonResponse({'status': 'success', 'message': 'User is authenticated'})
    # else:
    #     return JsonResponse({'status': 'error', 'message': 'User is not authenticated'})




    pass

    # from django.contrib.auth.models import User
    # user = User.objects.get(username='dast')
    # print(validate_user(user))


if __name__ == '__main__':
    run()

