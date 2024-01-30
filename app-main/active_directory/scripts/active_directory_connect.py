# load modules 
from dotenv import load_dotenv
import os
from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, ALL
from ldap3.core.exceptions import LDAPKeyError
# Load .env file
# Import load_dotenv
from dotenv import load_dotenv
dotenv_path = '/usr/src/project/.devcontainer/.env'
load_dotenv(dotenv_path=dotenv_path)





def active_directory_connect():
    try:
        ad_username = os.getenv('ACTIVE_DIRECTORY_USERNAME')
        ad_password = os.getenv('ACTIVE_DIRECTORY_PASSWORD')
        ad_server = os.getenv('ACTIVE_DIRECTORY_SERVER')

        # Connect to the server
        bind_dn = f"CN={ad_username},OU=AIT,OU=DTUBaseUsers,DC=win,DC=dtu,DC=dk"
        
        server = Server(ad_server, use_ssl=True, get_info=ALL)
        conn = Connection(server, bind_dn, ad_password)

        # Check if the connection is successful
        if not conn.bind():
            return None, "Failed to connect to Active Directory" 

        return conn, "Successfully connected to Active Directory", 
    except Exception as e:
        return None, f"Error connecting to Active Directory: {str(e)}"




def run():
    ad_connection_object, message = active_directory_connect()
    if message:
        print(message)




# if main 
if __name__ == "__main__":
    run()
