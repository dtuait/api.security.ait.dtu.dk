# load modules 
from dotenv import load_dotenv
import os
from ldap3 import Server, Connection, SUBTREE, ALL_ATTRIBUTES, ALL
from ldap3.core.exceptions import LDAPKeyError






def active_directory_connect():
    return "active_directory_connect"

def run():
    message = active_directory_connect()
    if message:
        print(message)




# if main 
if __name__ == "__main__":
    run()
