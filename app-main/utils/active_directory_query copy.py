
from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, ALL
from ldap3.core.exceptions import LDAPKeyError
from ldap3.utils.conv import escape_filter_chars
from utils.active_directory_connect import active_directory_connect
from ldap3.core.exceptions import LDAPException







def active_directory_query(base_dn, search_filter, search_attributes):
    try:
        conn, message = active_directory_connect()

        if not conn:
            print('Failed to connect to AD:', message)
            return []

        if not conn.bind():
            print('Error in bind', conn.result)
            return []

        ldap_list = []
        page_size = 500
        paged_cookie = None

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
                # Convert each entry to a dictionary of attributes

                attr_dict = {}
                for attr in search_attributes:
                    if attr in entry.entry_attributes_as_dict:
                        try:
                            attr_dict[attr] = entry.entry_attributes_as_dict[attr][0]
                        except (IndexError, KeyError):
                            attr_dict[attr] = ''
                    else:
                        raise ValueError(f"Attribute {attr} not found in entry")
                ldap_list.append(attr_dict)

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















# def active_directory_query(base_dn, search_filter, search_attributes):
#     conn, message = active_directory_connect()

#     if not conn:
#         print('Failed to connect to AD:', message)
#         return []

#     if not conn.bind():
#         print('Error in bind', conn.result)
#         return []
    
#     ldap_list = []
#     page_size = 500
#     paged_cookie = None

#     while True:
#         # Performing the paged search
#         conn.search(search_base=base_dn,
#                     search_filter=search_filter,
#                     search_scope=SUBTREE,
#                     attributes=search_attributes,
#                     paged_size=page_size,
#                     paged_cookie=paged_cookie)
        
#         # Process each entry in the current page
#         for entry in conn.entries:
#             # Convert each entry to a dictionary of attributes
            
#             attr_dict = {}
#             for attr in search_attributes:
#                 if attr in entry.entry_attributes_as_dict: # or attr in entry.entry_attributes_as_dict.lower() or attr in entry.entry_attributes_as_dict[attr.lower()] or attr in entry.entry_attributes_as_dict[attr.upper()]:
#                     attr_dict[attr] = entry.entry_attributes_as_dict[attr][0]
#                 else:
#                     raise ValueError(f"Attribute {attr} not found in entry")
#             ldap_list.append(attr_dict)

#         # Retrieve the cookie for the next page
#         paged_cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
#         if not paged_cookie:  # No more pages
#             break

#     conn.unbind()
#     return ldap_list




def run():
    # Example use case: Find if a specific user is a member of a specific group
    base_dn = 'DC=win,DC=dtu,DC=dk'
    user_name = 'adm-vicre'  # Example user
    group_dn = 'CN=ADM-ITAdm,OU=ITAdmSecurityGroups,OU=Delegations and Security,DC=win,DC=dtu,DC=dk'  # Example group
    search_filter = f'(&(objectClass=user)(sAMAccountName={user_name})(memberOf={group_dn}))'
    search_attributes = ['sAMAccountName']

    # Call the function
    result = active_directory_query(base_dn, search_filter, search_attributes)
    if result:
        print(f'User {user_name} is a member of the specified group.')
    else:
        print(f'User {user_name} is not a member of the specified group.')

if __name__ == "__main__":
    run()




# from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, ALL
# from ldap3.core.exceptions import LDAPKeyError
# from utils import active_directory_connect


# def active_directory_query(base_dn, search_filter, search_attributes):
#     conn, message = active_directory_connect.active_directory_connect()

#     if not conn:
#         print('Failed to connect to AD:', message)
#         return

#     if not conn.bind():
#         print('Error in bind', conn.result)
#         return
    
    
#     page_size = 500
#     paged_cookie = None
#     ldap_list = []

#     more_pages = True
#     while more_pages:
#         conn.search(search_base=base_dn,
#                     search_filter=search_filter,
#                     search_scope=SUBTREE,
#                     attributes=search_attributes,
#                     paged_size=page_size,
#                     paged_cookie=paged_cookie)

#         # Process each entry
#         for entry in conn.entries:
#             user_name = entry
#             ldap_list.append(user_name)

#         # Handle paging if there are more pages
#         more_pages = bool(conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie'])
#         if more_pages:
#             paged_cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
#         else:
#             paged_cookie = None

#     return ldap_list



# def run():
#     base_dn = 'DC=win,DC=dtu,DC=dk'
#     search_filter = '(objectClass=user)'
#     search_attributes = ['cn']






# # if main 
# if __name__ == "__main__":
#     run()
