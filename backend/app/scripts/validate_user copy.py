

def validate_user(user_principal_name: str, on_premises_immutable_id: str):

    from active_directory.services import execute_active_directory_query
    base_dn = "DC=win,DC=dtu,DC=dk"
    search_filter = f"(userPrincipalName={user_principal_name})"
    search_attributes = ['mS-DS-ConsistencyGuid',]
    active_directory_response = execute_active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

    ms_ds_consistency_guid = active_directory_response[0]['mS-DS-ConsistencyGuid'][0]
    import base64

    binary_guid = bytes(ms_ds_consistency_guid, 'raw_unicode_escape')
    base64_guid = base64.urlsafe_b64encode(binary_guid).decode('utf-8').rstrip('=')

    print(f'Base64 guid: {base64_guid}') # >> Base64 guid: QmkWP0JcOVR3AQ
    print(f'On premises immutable id: {on_premises_immutable_id}') # >> On premises immutable id: Qvlp7BbVP0KvXNE5VM13AQ==

    is_synced = (base64_guid == on_premises_immutable_id)
    print(f'Is the user synced? {is_synced}') # >> Is the user synced? False
        
    pass



def run():
    from graph.services import execute_get_user
    from django.http import JsonResponse

    # This part is equal to when the user has authenticated via msal
    select_param = '$select=onPremisesImmutableId,userPrincipalName'
    user = 'vicre@dtu.dk'
    response, status_code = execute_get_user(user, select_param)
    user_principal_name = response['userPrincipalName']
    on_premises_immutable_id = response.get('onPremisesImmutableId')



    django_user = validate_user(user_principal_name=user_principal_name, on_premises_immutable_id=on_premises_immutable_id)


    if django_user is not None:
        return JsonResponse({'status': 'success', 'message': 'User is authenticated'})
    else:
        return JsonResponse({'status': 'error', 'message': 'User is not authenticated'})




    pass

    # from django.contrib.auth.models import User
    # user = User.objects.get(username='dast')
    # print(validate_user(user))


if __name__ == '__main__':
    run()

