
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




def active_directory_query(base_dn, search_filter, search_attributes=None, limit=None):
    try:
        conn, message = active_directory_connect()

        if not conn:
            print('Failed to connect to AD:', message)
            return []

        if not conn.bind():
            print('Error in bind', conn.result)
            return []

        ldap_list = []
        # If limit is None or greater than 500, use 500 as the page size; otherwise, use limit.
        page_size = 500 if limit is None or limit > 500 else limit
        paged_cookie = None
        entries_collected = 0

        while True:
            # Performing the paged search
            conn.search(search_base=base_dn,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=search_attributes,
                        paged_size=page_size,
                        paged_cookie=paged_cookie)

            # Process each entry in the current page
            for entry in conn.entries:
                if limit is not None and entries_collected >= limit:
                    break  # Stop if we've reached the limit and limit is not None (unlimited)

                # Convert each entry to a dictionary of attributes
                if search_attributes is None:
                    # If search_attributes is None, add all attributes from the entry
                    # attr_dict = entry.entry_attributes_as_dict
                    attr_dict = entry
                else:
                    # Otherwise, proceed with filtering the specified attributes
                    attr_dict = {}
                    for attr in search_attributes:
                        attr_values = entry.entry_attributes_as_dict.get(attr, [])
                        if attr_values:  # Check if the attribute has at least one value
                            attr_dict[attr] = attr_values[0]
                        else:
                            attr_dict[attr] = None  # Or use '' if you prefer an empty string for missing/empty attributes


                ldap_list.append(attr_dict)
                entries_collected += 1

            if limit is not None and entries_collected >= limit:
                break  # Exit the while loop if the limit is reached and is not None

            # Retrieve the cookie for the next page
            if conn.result['controls'] and '1.2.840.113556.1.4.319' in conn.result['controls']:
                paged_cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
                if not paged_cookie:  # No more pages
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
    search_attributes = None  # All attributes
    limit = None  # Unlimited



    # users_all = active_directory_query(base_dn, search_filter, search_attributes, limit)
    # print(len(users_all))

    
    limit = 100  # Limit to first 100 users
    # Call the function
    users_first_100 = active_directory_query(base_dn, search_filter, search_attributes, limit)
    print(len(users_first_100))
    print(users_first_100[0].entry_dn)

    search_attributes = ['entry_dn']
    users_first_100_with_attributes = active_directory_query(base_dn, search_filter, search_attributes, limit)
    print(len(users_first_100_with_attributes))
    print(users_first_100_with_attributes[0].entry_dn)

    search_filter = "(objectClass=computer)"
    search_attributes = ["cn", "operatingSystem"]
    limit = None  # Unlimited

    # Call the function
    computers_all = active_directory_query(base_dn, search_filter, search_attributes, limit)

    print(len(computers_all))

    search_filter = "(objectClass=group)"
    search_attributes = ["cn", "description"]
    limit = None  # Unlimited

    # Call the function
    groups_all = active_directory_query(base_dn, search_filter, search_attributes, limit)

    print(len(groups_all))

    limit = 100  # Limit to first 100 groups

    # Call the function
    groups_first_100 = active_directory_query(base_dn, search_filter, search_attributes, limit)

    print(len(groups_first_100))


    print('Done')

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


