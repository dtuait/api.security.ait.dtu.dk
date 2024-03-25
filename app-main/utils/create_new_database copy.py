from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from dotenv import load_dotenv
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
from ldap3 import Server, Connection, ALL, SUBTREE
from utils.active_directory_query import active_directory_query
import string
from django.contrib.auth.hashers import make_password, check_password
import random
from myview.models import ADGroupAssociation
from utils.cronjob_update_endpoints import updateEndpoints
import shutil


class Command(BaseCommand):
    def reset_database(self, *args, **options):


        try:

      
            self._reset_database(create_back=False)
            self.startmake_migrations(None,None)
            self.startmigrate(None,None)
            self.createsuperuser(None,None)
            self.createnormalusers(None,None)
            self.createalladgroups(None,None)
            updateEndpoints()
            

        except Exception as e:
            print(f"An error occurred: {e}")


    def _reset_database(self, create_back=True, *args, **options):
        # Load environment variables
        dotenv_path = '/usr/src/project/.devcontainer/.env'
        load_dotenv(dotenv_path=dotenv_path)

        # Configuration
        config = {
            "host": os.getenv("MYSQL_HOST"),
            "user": os.getenv("MYSQL_ROOT_USER"),
            "password": os.getenv("MYSQL_ROOT_PASSWORD"),
        }

        # Connect to MariaDB
        conn = pymysql.connect(**config)
        cursor = conn.cursor()

        # Generate new database name with timestamp if create_back is True
        if create_back:
            copenhagen_tz = pytz.timezone('Europe/Copenhagen')
            timestamp = datetime.now(copenhagen_tz).strftime('%Y_%m_%d_%H_%M_%S')
            old_db_name = os.getenv("MYSQL_DATABASE")
            new_db_name = f"{timestamp}_{old_db_name}"

            # Rename the old database by creating a new one and moving tables
            cursor.execute(f"CREATE DATABASE `{new_db_name}`;")
            cursor.execute(f"SHOW TABLES IN `{old_db_name}`;")
            tables = cursor.fetchall()
            for (table_name,) in tables:
                cursor.execute(f"RENAME TABLE `{old_db_name}`.`{table_name}` TO `{new_db_name}`.`{table_name}`;")
            
            # Move migrations directory if exists
            migrations_dir = '/usr/src/project/app-main/myview/migrations'
            new_migrations_dir = f'/usr/src/project/app-main/myview/migrations_{timestamp}.bak'
            if os.path.exists(migrations_dir):
                os.rename(migrations_dir, new_migrations_dir)
        else:
            # If create_back is False, just get the database name without timestamp
            old_db_name = os.getenv("MYSQL_DATABASE")

        # Drop the current database and create a new one with the same name
        cursor.execute(f"DROP DATABASE IF EXISTS `{old_db_name}`;")
        cursor.execute(f"CREATE DATABASE `{old_db_name}`;")

        # If create_back is False, also delete the migrations directory
        if not create_back:
            migrations_dir = '/usr/src/project/app-main/myview/migrations'
            if os.path.exists(migrations_dir):
                shutil.rmtree(migrations_dir)  # This removes the directory and all its contents

        cursor.close()
        conn.close()

    # def createalladgroups(self, *args, **options):
    #     base_dn = "DC=win,DC=dtu,DC=dk"
    #     search_filter = "(objectClass=group)"
    #     search_attributes = ['CN', 'CanonicalName', 'DistinguishedName']
    #     ad_groups = self.perform_ldap_search(base_dn, search_filter, search_attributes)
    #     print(ad_groups)



    #     Group = get_user_model()
    #     new_groups = []
            
    def createalladgroups(self, *args, **options):
        ADGroupAssociation.sync_ad_groups(self)
        # base_dn = "DC=win,DC=dtu,DC=dk"
        # search_filter = "(objectClass=group)"
        # search_attributes = ['cn', 'canonicalName', 'distinguishedName']
        # ad_groups = self.perform_ldap_search(base_dn, search_filter, search_attributes)

        # new_ad_groups = []  # To collect new AD groups
        # for ad_group in ad_groups:
        #     # cn = ad_group.entry_attributes_as_dict['cn'][0] # >> Server Management
        #     # canonical_name = ad_group.entry_attributes_as_dict['canonicalName'][0] # >> win.dtu.dk/Microsoft Exchange Security Groups/Exchange Servers
        #     # distinguished_name = ad_group.entry_attributes_as_dict['distinguishedName'][0] # >> CN=Exchange Servers,OU=Microsoft Exchange Security Groups,DC=win,DC=dtu,DC=dk

        #     cn = ad_group['cn'] # >> Server Management
        #     canonical_name = ad_group['canonicalName'] # >> win.dtu.dk/Microsoft Exchange Security Groups/Exchange Servers
        #     distinguished_name = ad_group['distinguishedName'] # >> CN=Exchange Servers,OU=Microsoft Exchange Security Groups,DC=win,DC=dtu,DC=dk

        #     # Create a new ADGroup instance for each group
        #     new_group = ADGroupAssociation(cn=cn, canonical_name=canonical_name, distinguished_name=distinguished_name)
        #     new_ad_groups.append(new_group)

        # # Bulk create new AD groups
        # ADGroupAssociation.objects.bulk_create(new_ad_groups)
        print("done creating AD groups")

    def startmake_migrations(self, *args, **options):
        os.system('python /usr/src/project/app-main/manage.py makemigrations')
        os.system('python /usr/src/project/app-main/manage.py makemigrations myview')

    def startmigrate(self, *args, **options):
        os.system('python /usr/src/project/app-main/manage.py migrate')        



    def createnormalusers(self, *args, **options):

        base_dn = "DC=win,DC=dtu,DC=dk"
        search_filter = "(&(objectClass=user)(SamAccountName=adm-*))"
        search_attributes = ['distinguishedName', 'sAMAccountName', 'givenName', 'sn']
        adm_users = self.perform_ldap_search(base_dn, search_filter, search_attributes)

        try:

            ADGroupAssociation.create_new_users_if_not_exists(self, adm_users)

            # User = get_user_model()
            # new_users = []  # To collect new users

            # for adm_user in adm_users:
            #     username = adm_user['sAMAccountName'].lower() # adm-vicre

            #     if not User.objects.filter(username=username).exists():
                    
                    
            #         # Directly create a new user instance without checking for existence
            #         username_part = username.rsplit('-', 1)[-1]
            #         email = f'{username_part}@dtu.dk'
            #         is_superuser = username in ['adm-vicre', 'adm-jaholm']  # Set True for specific usernames
            #         is_staff = is_superuser  # Typically, superusers are also staff
                    
            #         new_user = User(username=username, email=email, is_superuser=is_superuser, is_staff=is_staff)
                    
            #         new_users.append(new_user)

            # User.objects.bulk_create(new_users)
            print("done creating normal users")

        except Exception as e:
            print(f"An error occurred during the LDAP operation: {e}")


    # def createnormalusers(self, *args, **options):

    #     base_dn = "DC=win,DC=dtu,DC=dk"
    #     search_filter = "(&(objectClass=user)(SamAccountName=adm-*))"
    #     search_attributes = ["sAMAccountName"]
    #     adm_users = self.perform_ldap_search(base_dn, search_filter, search_attributes)

    #     User = get_user_model()
    #     new_users = []  # To collect new users

    #     for adm_user in adm_users:
    #         username = adm_user['sAMAccountName'].lower() # adm-vicre

    #         if not User.objects.filter(username=username).exists():
                
                
    #             # Directly create a new user instance without checking for existence
    #             username_part = username.rsplit('-', 1)[-1]
    #             email = f'{username_part}@dtu.dk'
    #             is_superuser = username in ['adm-vicre', 'adm-jaholm']  # Set True for specific usernames
    #             is_staff = is_superuser  # Typically, superusers are also staff
                
    #             new_user = User(username=username, email=email, is_superuser=is_superuser, is_staff=is_staff)
                
    #             new_users.append(new_user)

    #     User.objects.bulk_create(new_users)
    #     print("done creating normal users")


    def createsuperuser(self, *args, **options):
        load_dotenv(dotenv_path='/usr/src/project/.devcontainer/.env')
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')


        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if not check_password(password, user.password):
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS('Superuser password updated'))
        except User.DoesNotExist:
            User.objects.create_superuser(username, 'vicre@dtu.dk', password)
            self.stdout.write(self.style.SUCCESS('Superuser created'))



    def generate_alphanumeric_password(self, length):
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for i in range(length))
        return password




    def perform_ldap_search(self, base_dn, search_filter, search_attributes):

        return active_directory_query(base_dn, search_filter, search_attributes)
                
        # conn, message = active_directory_connect.active_directory_connect()

        # if not conn:
        #     print('Failed to connect to AD:', message)
        #     return

        # if not conn.bind():
        #     print('Error in bind', conn.result)
        #     return
        
        
        # page_size = 500
        # paged_cookie = None
        # ldap_list = []

        # more_pages = True
        # while more_pages:
        #     conn.search(search_base=base_dn,
        #                 search_filter=search_filter,
        #                 search_scope=SUBTREE,
        #                 attributes=search_attributes,
        #                 paged_size=page_size,
        #                 paged_cookie=paged_cookie)

        #     # Process each entry
        #     for entry in conn.entries:
        #         user_name = entry
        #         ldap_list.append(user_name)

        #     # Handle paging if there are more pages
        #     more_pages = bool(conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie'])
        #     if more_pages:
        #         paged_cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        #     else:
        #         paged_cookie = None

        # return ldap_list



def run():
    command = Command()
    command.reset_database(None, None)
    print('done')

# if main 
if __name__ == "__main__":
    run()
























































#  def _reset_database(self, *args, **options):

#         # Load environment variables
#         dotenv_path = '/usr/src/project/.devcontainer/.env'
#         load_dotenv(dotenv_path=dotenv_path)

#         # Configuration
#         config = {
#             "host": os.getenv("MYSQL_HOST"),
#             "user": os.getenv("MYSQL_ROOT_USER"),
#             "password": os.getenv("MYSQL_ROOT_PASSWORD"),
#         }

#         # Generate new database name with timestamp
#         copenhagen_tz = pytz.timezone('Europe/Copenhagen')
#         timestamp = datetime.now(copenhagen_tz).strftime('%Y_%m_%d_%H_%M_%S')
#         old_db_name = os.getenv("MYSQL_DATABASE")
#         new_db_name = f"{timestamp}_{old_db_name}"


#         # Connect to MariaDB
#         conn = pymysql.connect(**config)
#         cursor = conn.cursor()

#         # Rename the old database by creating a new one and moving tables
#         cursor.execute(f"CREATE DATABASE `{new_db_name}`;")
#         cursor.execute(f"SHOW TABLES IN `{old_db_name}`;")
#         tables = cursor.fetchall()
#         for (table_name,) in tables:
#             cursor.execute(f"RENAME TABLE `{old_db_name}`.`{table_name}` TO `{new_db_name}`.`{table_name}`;")
#         cursor.execute(f"DROP DATABASE `{old_db_name}`;")

#         # Create a new database with the original name
#         cursor.execute(f"CREATE DATABASE `{old_db_name}`;")

#         cursor.close()
#         conn.close()

#         # check if /usr/src/project/app-main/myview/migrations exists and move it to /usr/src/project/app-main/myview/migrations_{timestamp}
#         migrations_dir = '/usr/src/project/app-main/myview/migrations'
#         new_migrations_dir = f'/usr/src/project/app-main/myview/migrations_{timestamp}.bak'
#         if os.path.exists(migrations_dir):
#             os.rename(migrations_dir, new_migrations_dir)
