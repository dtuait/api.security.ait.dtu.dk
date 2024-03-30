from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from dotenv import load_dotenv
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
from active_directory.scripts.active_directory_query import active_directory_query
import string
from django.contrib.auth.hashers import make_password, check_password
import random
from myview.models import ADGroupAssociation
from utils.cronjob_update_endpoints import updateEndpoints
import shutil
from django.contrib.auth.models import User


class Command(BaseCommand):
    def reset_database(self, *args, **options):


        try:

      
            self._reset_database(create_back=False)
            self.startmake_migrations(None,None)
            self.startmigrate(None,None)
            self.createsuperuser(None,None)
            self.createnormalusers(None,None)
            self.createalladgroups(None,None)

            ##### 
            django_init_token = os.getenv("DJANGO_ADM_VICRE_INIT_TOKEN")
            user = User.objects.get(username='adm-vicre')
            user.set_my_token(django_init_token)

            # django_init_token = os.getenv("DJANGO_ADM_DAST_INIT_TOKEN")
            # user = User.objects.get(username='adm-byg-dast')
            # user.set_my_token(django_init_token)
            
            # try:
            #     # Get the user
            #     user = User.objects.get(username='adm-vicre')
            #     # Get the existing token
            #     token = Token.objects.get(user=user)
            #     # Delete the old token
            #     token.delete()
            # except User.DoesNotExist:
            #     print("User 'adm-vicre' does not exist.")
            # except Token.DoesNotExist:
            #     pass

            # # Create a new token
            # Token.objects.create(user=user, key=django_init_token)

            #######
            updateEndpoints()
            

        except Exception as e:
            print(f"An error occurred: {e}")


    def give_all_users_a_token(self, *args, **options):
        from myview.models import CustomToken

        User = get_user_model()
        users = User.objects.all()
        for user in users:
            if not user.auth_token:
                token = self.generate_alphanumeric_password(30)
                user.auth_token = make_password(token)
                user.save()
        print("done giving all users a token")


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


    def createalladgroups(self, *args, **options):
        ADGroupAssociation.sync_ad_groups(self)
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
            print("done creating normal users")

        except Exception as e:
            print(f"An error occurred during the LDAP operation: {e}")


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

        return active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes, limit=None)
   

def run():
    command = Command()
    command.reset_database(None, None)
    print('done')

# if main 
if __name__ == "__main__":
    run()

