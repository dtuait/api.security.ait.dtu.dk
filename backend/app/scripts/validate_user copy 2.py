

def validate_user(user_principal_name: str, on_premises_immutable_id: str):
    from active_directory.services import execute_active_directory_query
    base_dn = "DC=win,DC=dtu,DC=dk"
    search_filter = f"(userPrincipalName={user_principal_name})"
    search_attributes = ['mS-DS-ConsistencyGuid', 'userPrincipalName']
    active_directory_response = execute_active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

    ms_ds_consistency_guid = active_directory_response[0]['mS-DS-ConsistencyGuid'][0]
    ad_user_principal_name = active_directory_response[0]['userPrincipalName'][0]
    import base64

    # Convert the GUID from the escaped Unicode format to bytes
    binary_guid = bytes(ms_ds_consistency_guid, 'raw_unicode_escape')

    # Debug: print raw binary to understand what's being encoded
    print(f'Raw binary GUID: {binary_guid}')

    # Encode to Base64 (standard version, not URL-safe, with padding for comparison)
    base64_guid = base64.b64encode(binary_guid).decode('utf-8')

    print(f'AD User Principal Name: {ad_user_principal_name}')
    print(f'Base64 GUID (from AD, with padding): {base64_guid}')
    print(f'Azure User Principal Name: {user_principal_name}')
    print(f'Azure On Premises Immutable ID (expected to match): {on_premises_immutable_id}')

    # Compare the two base64 strings
    is_synced = (base64_guid == on_premises_immutable_id)
    print(f'Is the user synced? {is_synced}')
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

