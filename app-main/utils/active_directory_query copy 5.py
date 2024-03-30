
from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, ALL
from ldap3.core.exceptions import LDAPKeyError
from ldap3.utils.conv import escape_filter_chars
from utils.active_directory_connect import active_directory_connect
from ldap3.core.exceptions import LDAPException







# def active_directory_query(base_dn, search_filter, search_attributes):
#     try:
#         conn, message = active_directory_connect()

#         if not conn:
#             print('Failed to connect to AD:', message)
#             return []

#         if not conn.bind():
#             print('Error in bind', conn.result)
#             return []

#         ldap_list = []
#         page_size = 500
#         paged_cookie = None

#         while True:
#             # Performing the paged search
#             conn.search(search_base=base_dn,
#                         search_filter=search_filter,
#                         search_scope=SUBTREE,
#                         attributes=search_attributes,
#                         paged_size=page_size,
#                         paged_cookie=paged_cookie)

#             # Process each entry in the current page
#             for entry in conn.entries:
#                 # Convert each entry to a dictionary of attributes

#                 attr_dict = {}
#                 for attr in search_attributes:
#                     if attr in entry.entry_attributes_as_dict:
#                         try:
#                             attr_dict[attr] = entry.entry_attributes_as_dict[attr][0]
#                         except (IndexError, KeyError):
#                             attr_dict[attr] = ''
#                     else:
#                         raise ValueError(f"Attribute {attr} not found in entry")
#                 ldap_list.append(attr_dict)

#             # Retrieve the cookie for the next page
#             if conn.result['controls'] and '1.2.840.113556.1.4.319' in conn.result['controls']:
#                 paged_cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
#                 if not paged_cookie:  # No more pages
#                     break
#             else:
#                 print('Paged search control not found in server response.')
#                 break

#         conn.unbind()
#         return ldap_list

#     except LDAPException as error:
#         print(f"An error occurred during the LDAP operation: {error}")
#         return []
#     except Exception as error:
#         print(f"An unexpected error occurred: {error}")
#         return []


# def active_directory_query(base_dn, search_filter, search_attributes, limit=100):
#     try:
#         conn, message = active_directory_connect()

#         if not conn:
#             print('Failed to connect to AD:', message)
#             return []

#         if not conn.bind():
#             print('Error in bind', conn.result)
#             return []

#         ldap_list = []
#         page_size = min(500, limit)  # Adjust the page size if limit is lower
#         paged_cookie = None
#         entries_collected = 0

#         while True:
#             # Performing the paged search
#             conn.search(search_base=base_dn,
#                         search_filter=search_filter,
#                         search_scope=SUBTREE,
#                         attributes=search_attributes,
#                         paged_size=page_size,
#                         paged_cookie=paged_cookie)

#             # Process each entry in the current page
#             for entry in conn.entries:
#                 if entries_collected >= limit:
#                     break  # Stop if we've reached the limit

#                 # Convert each entry to a dictionary of attributes
#                 attr_dict = {}
#                 for attr in search_attributes:
#                     if attr in entry.entry_attributes_as_dict:
#                         try:
#                             attr_dict[attr] = entry.entry_attributes_as_dict[attr][0]
#                         except (IndexError, KeyError):
#                             attr_dict[attr] = ''
#                     else:
#                         raise ValueError(f"Attribute {attr} not found in entry")
#                 ldap_list.append(attr_dict)
#                 entries_collected += 1

#             if entries_collected >= limit:
#                 break  # Exit the while loop if the limit is reached

#             # Retrieve the cookie for the next page
#             if conn.result['controls'] and '1.2.840.113556.1.4.319' in conn.result['controls']:
#                 paged_cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
#                 if not paged_cookie:  # No more pages
#                     break
#             else:
#                 print('Paged search control not found in server response.')
#                 break

#         conn.unbind()
#         return ldap_list

#     except LDAPException as error:
#         print(f"An error occurred during the LDAP operation: {error}")
#         return []
#     except Exception as error:
#         print(f"An unexpected error occurred: {error}")
#         return []



def active_directory_query(*, base_dn, search_filter, search_attributes=ALL_ATTRIBUTES, limit=None):
    try:
        conn, message = active_directory_connect()

        if not conn:
            print('Failed to connect to AD:', message)
            return []

        if not conn.bind():
            print('Error in bind', conn.result)
            return []

        ldap_list = []
        page_size = 500 if limit is None or limit > 500 else limit
        paged_cookie = None
        entries_collected = 0

        # If search_attributes is None, use ALL_ATTRIBUTES to get all
        attributes_to_fetch = ALL_ATTRIBUTES if search_attributes is ALL_ATTRIBUTES else search_attributes

        while True:
            conn.search(search_base=base_dn,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=attributes_to_fetch,
                        paged_size=page_size,
                        paged_cookie=paged_cookie)

            for entry in conn.entries:
                if limit is not None and entries_collected >= limit:
                    break

                if search_attributes is None or search_attributes == ALL_ATTRIBUTES:
                    # When fetching all attributes, convert the entire entry to a dict
                    attr_dict = {attr: value for attr, value in entry.entry_attributes_as_dict.items()}
                else:
                    attr_dict = {}
                    for attr in search_attributes:
                        attr_values = entry.entry_attributes_as_dict.get(attr, [])
                        attr_dict[attr] = attr_values[0] if attr_values else None

                ldap_list.append(attr_dict)
                entries_collected += 1

                if limit is not None and entries_collected >= limit:
                    break

            if limit is not None and entries_collected >= limit:
                break

            if conn.result['controls'] and '1.2.840.113556.1.4.319' in conn.result['controls']:
                paged_cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
                if not paged_cookie:
                    break
            else:
                print('Paged search control not found in server response.')
                break

        conn.unbind()
        return ldap_list

    except LDAPException as error:
        print(f"An error occurred during the LDAP operation: {error}")
        return []
    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        return []





def run():

    # class ADGroupAssociation(BaseModel):
    # cn = models.CharField(max_length=255, verbose_name="Common Name")
    # canonical_name = models.CharField(max_length=1024)
    # distinguished_name = models.CharField(max_length=1024)
    # members = models.ManyToManyField(User, related_name='ad_groups')

    

    from myview.models import ADGroupAssociation

    # def get_ad_group():
    #     try:
    #         ad_group = ADGroupAssociation.objects.get(canonical_name='win.dtu.dk/Institutter/SUS/Groups/IT/SUS-MFA-Reset')
    #         return ad_group
    #     except ADGroupAssociation.DoesNotExist:
    #         print("ADGroupAssociation with the specified canonical_name does not exist.")

    # ad_group = get_ad_group()

    # # distinguished_name:'CN=SUS-MFA-Reset,OU=IT,OU=Groups,OU=SUS,OU=Institutter,DC=win,DC=dtu,DC=dk'
    # # canonicalName=win.dtu.dk/Institutter/SUS/Groups/IT/SUS-MFA-Reset

    # base_dn = 'DC=win,DC=dtu,DC=dk'
    # search_filter = '(canonicalName=win.dtu.dk/Institutter/SUS/Groups/IT/SUS-MFA-Reset*)'
    # search_attributes = ['canonicalName']


    base_dn = "DC=win,DC=dtu,DC=dk"
    search_filter = "(objectClass=user)"
    limit = 100  # Limit to first 100 users
    users_first_100 = active_directory_query(base_dn=base_dn, search_filter=search_filter, limit=limit)
    print(len(users_first_100))
    print(users_first_100[0]['distinguishedName']) # ['CN=Exchange Online-ApplicationAccount,OU=Users,OU=MailogKalender,OU=BIT-DSG,OU=AIT,DC=win,DC=dtu,DC=dk']
    

    search_attributes = ['cn', 'mail', 'sAMAccountName', 'distinguishedName', 'userPrincipalName', 'memberOf']
    users_first_100_with_attributes = users_first_100 = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=limit)
    print(len(users_first_100_with_attributes))
    print(users_first_100_with_attributes[0]['distinguishedName']) # >> CN=Exchange Online-ApplicationAccount,OU=Users,OU=MailogKalender,OU=BIT-DSG,OU=AIT,DC=win,DC=dtu,DC=dk
    

    search_filter = "(objectClass=computer)"
    limit = 100  

    computers_first_100 = active_directory_query(base_dn=base_dn, search_filter=search_filter, limit=limit)
    print(len(computers_first_100))
    print(computers_first_100[0]['distinguishedName'])

    search_attributes = ['cn', 'description', 'distinguishedName', 'operatingSystem', 'operatingSystemVersion']
    computers_first_100_with_attributes = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=limit)
    print(len(computers_first_100_with_attributes))
    print(computers_first_100_with_attributes[0]['distinguishedName'])


    # get first 100 groups
    search_filter = "(objectClass=group)"
    limit = 100 
    groups_first_100 = active_directory_query(base_dn=base_dn, search_filter=search_filter, limit=limit)
    print(len(groups_first_100))
    print(groups_first_100[0]['distinguishedName'])

    search_attributes = ['cn', 'description', 'distinguishedName', 'member']
    groups_first_100_with_attributes = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=limit)
    print(len(groups_first_100_with_attributes))
    print(groups_first_100_with_attributes[0]['distinguishedName'])








    print('Done')












    # # Call the function
    # computers_all = active_directory_query(base_dn, search_filter, search_attributes, limit)
    # print(len(computers_all))

    # search_filter = "(objectClass=group)"
    # search_attributes = ["cn", "description"]
    # limit = None  # Unlimited

    # # Call the function
    # groups_all = active_directory_query(base_dn, search_filter, search_attributes, limit)

    # print(len(groups_all))

    # limit = 100  # Limit to first 100 groups

    # # Call the function
    # groups_first_100 = active_directory_query(base_dn, search_filter, search_attributes, limit)

    # print(len(groups_first_100))


    # print('Done')

    # # Get the first 100 AD objects that match the search filter
    # ad_objects = active_directory_query(base_dn, search_filter, search_attributes)

    # for obj in ad_objects:
    #     print(obj)

    # Example use case: Find if a specific user is a member of a specific group
    # base_dn = 'DC=win,DC=dtu,DC=dk'
    # user_name = 'adm-vicre'  # Example user
    # group_dn = 'CN=ADM-ITAdm,OU=ITAdmSecurityGroups,OU=Delegations and Security,DC=win,DC=dtu,DC=dk'  # Example group
    # search_filter = f'(&(objectClass=user)(sAMAccountName={user_name})(memberOf={group_dn}))'
    # search_attributes = ['sAMAccountName']

    #     # Call the function
    # result = active_directory_query(base_dn, search_filter, search_attributes)
    # if result:
    #     print(f'User {user_name} is a member of the specified group.')
    # else:
    #     print(f'User {user_name} is not a member of the specified group.')

if __name__ == "__main__":
    run()


