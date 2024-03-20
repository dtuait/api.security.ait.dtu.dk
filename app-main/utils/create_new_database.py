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
from utils import active_directory_connect
import string
from django.contrib.auth.hashers import make_password, check_password
import random
class Command(BaseCommand):
    def handle(self, *args, **options):


        try:

            # Load environment variables
            dotenv_path = '/usr/src/project/.devcontainer/.env'
            load_dotenv(dotenv_path=dotenv_path)

            # Configuration
            config = {
                "host": os.getenv("MYSQL_HOST"),
                "user": os.getenv("MYSQL_ROOT_USER"),
                "password": os.getenv("MYSQL_ROOT_PASSWORD"),
            }

            # Generate new database name with timestamp
            copenhagen_tz = pytz.timezone('Europe/Copenhagen')
            timestamp = datetime.now(copenhagen_tz).strftime('%Y_%m_%d_%H_%M_%S')
            old_db_name = os.getenv("MYSQL_DATABASE")
            new_db_name = f"{timestamp}_{old_db_name}"


            # Connect to MariaDB
            conn = pymysql.connect(**config)
            cursor = conn.cursor()

            # Rename the old database by creating a new one and moving tables
            cursor.execute(f"CREATE DATABASE `{new_db_name}`;")
            cursor.execute(f"SHOW TABLES IN `{old_db_name}`;")
            tables = cursor.fetchall()
            for (table_name,) in tables:
                cursor.execute(f"RENAME TABLE `{old_db_name}`.`{table_name}` TO `{new_db_name}`.`{table_name}`;")
            cursor.execute(f"DROP DATABASE `{old_db_name}`;")

            # Create a new database with the original name
            cursor.execute(f"CREATE DATABASE `{old_db_name}`;")

            cursor.close()
            conn.close()

            # check if /usr/src/project/app-main/myview/migrations exists and move it to /usr/src/project/app-main/myview/migrations_{timestamp}
            migrations_dir = '/usr/src/project/app-main/myview/migrations'
            new_migrations_dir = f'/usr/src/project/app-main/myview/migrations_{timestamp}.bak'
            if os.path.exists(migrations_dir):
                os.rename(migrations_dir, new_migrations_dir)

            self.startmake_migrations(None,None)
            self.startmigrate(None,None)
            self.createsuperuser(None,None)
            self.createnormalusers(None,None)

        except Exception as e:
            print(f"An error occurred: {e}")

    def startmake_migrations(self, *args, **options):
        os.system('python /usr/src/project/app-main/manage.py makemigrations')

    def startmigrate(self, *args, **options):
        os.system('python /usr/src/project/app-main/manage.py migrate')        


    def createnormalusers(self, *args, **options):
        # # List of normal users and their passwords
        # users = {
        #     'adm-vicre': '28ZLNd3jx5naUap8xjmaRL3HqFPA3Xbv',
        #     'adm-jaholm': '28ZLNd3jx5naUap8xjmaRL3HqFPA3Xbv',
        #     'adm-dast': '28ZLNd3jx5naUap8xjmaRL3HqFPA3Xbv'
        # }
        base_dn = "DC=win,DC=dtu,DC=dk"
        search_filter = "(&(objectClass=user)(SamAccountName=adm-*))"
        search_attributes = ["SamAccountName"]
        adm_users = self.perform_ldap_search(base_dn, search_filter, search_attributes)
        # print("Admin Users:", adm_users)

        User = get_user_model()
        new_users = []  # To collect new users

        for adm_user in adm_users:
            username = adm_user.entry_attributes_as_dict['sAMAccountName'][0].lower()

            if not User.objects.filter(username=username).exists():
                
                
                # Directly create a new user instance without checking for existence
                username_part = username.rsplit('-', 1)[-1]
                email = f'{username_part}@dtu.dk'
                is_superuser = username in ['adm-vicre', 'adm-jaholm']  # Set True for specific usernames
                is_staff = is_superuser  # Typically, superusers are also staff
                
                new_user = User(username=username, email=email, is_superuser=is_superuser, is_staff=is_staff)
                
                new_users.append(new_user)

        User.objects.bulk_create(new_users)
        print("done creating normal users")
            # username = adm_user.entry_attributes_as_dict['sAMAccountName'][0]
            # # new_user = User(username=username, email=f'{username}@win.dtu.dk')
            # # new_users.append(new_user)
            
            # # Check if a user already exists with the given username
            # if not User.objects.filter(username=username).exists():
            #     # Create a new user instance without setting a password

            #     # if username == 'adm-vicre' or username == 'adm-jaholm' make it a superuser else a normal user
            #     if username == 'adm-vicre' or username == 'adm-jaholm':
            #         new_user = User(username=username, email=f'{username}@win.dtu.dk')
            #         new_user.is_superuser(True)  # Assuming you have a set_superuser method
            #     else:
            #         new_user = User(username=username, email=f'{username}@win.dtu.dk')

            #     new_users.append(new_user)

        # # Bulk create new users without setting passwords
        # User.objects.bulk_create(new_users)
        # print("done creating normal users")
        # User = get_user_model()
        # new_users = [] # To collect new users
        # users_to_update = [] # To collect users whose password needs updating


        # User = get_user_model()
        # for adm_user in adm_users:
        #     username = adm_user.entry_attributes_as_dict['sAMAccountName'][0]
        #     password = self.generate_alphanumeric_password(105)  # Assuming this method exists within the same class
            
        #     try:
        #         user = User.objects.get(username=username)
        #         if not check_password(password, user.password):
        #             user.password = make_password(password)
        #             users_to_update.append(user)
        #     except User.DoesNotExist:
        #         user = User(username=username, email=f'{username}@win.dtu.dk')
        #         user.password = make_password(password)
        #         new_users.append(user)
        
        # # Bulk create new users
        # User.objects.bulk_create(new_users)


        # # For updating, since each user needs their password hashed (which bulk_update doesn't support for individual call), we save them individually.
        # # If the number of users to update is significantly large, consider a more efficient strategy or background processing.
        # for user in users_to_update:
        #     user.save()  # This is not bulk update, but necessary for password hashing

        # # You can still print successes, but consider doing so after bulk operations to minimize console I/O time.
        # for user in new_users:
        #     self.stdout.write(self.style.SUCCESS(f'User {user.username} created'))

        # for user in users_to_update:
        #     self.stdout.write(self.style.SUCCESS(f'Password updated for user {user.username}'))

            # try:
            #     username = adm_user.entry_attributes_as_dict['sAMAccountName'][0]
            #     password = self.generate_alphanumeric_password(105)

            #     #                 # Generate a 66-character long alphanumeric password
            #     # alphanumeric_password = generate_alphanumeric_password(66)
            #     # alphanumeric_password

            #     user = User.objects.get(username=username)
            #     if not check_password(password, user.password):
            #         user.set_password(password)
            #         user.save()
            #         self.stdout.write(self.style.SUCCESS(f'Password updated for user {username}'))
            #     pass
            # except User.DoesNotExist:
            #     User.objects.create_user(username, f'{username}@example.com', password)
            #     self.stdout.write(self.style.SUCCESS(f'User {username} created'))
            #     pass


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
        
        
        conn, message = active_directory_connect.active_directory_connect()

        if not conn:
            print('Failed to connect to AD:', message)
            return

        if not conn.bind():
            print('Error in bind', conn.result)
            return
        
        
        page_size = 500
        paged_cookie = None
        ldap_list = []

        more_pages = True
        while more_pages:
            conn.search(search_base=base_dn,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=search_attributes,
                        paged_size=page_size,
                        paged_cookie=paged_cookie)

            # Process each entry
            for entry in conn.entries:
                user_name = entry
                ldap_list.append(user_name)

            # Handle paging if there are more pages
            more_pages = bool(conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie'])
            if more_pages:
                paged_cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            else:
                paged_cookie = None

        return ldap_list



def run():
    command = Command()
    command.handle(None, None)
    print('done')

# if main 
if __name__ == "__main__":
    run()
