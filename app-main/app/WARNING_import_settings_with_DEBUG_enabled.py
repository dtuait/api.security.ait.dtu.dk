from .settings import *
from termcolor import colored
import getpass

DEBUG = True

if DEBUG:
    current_user = getpass.getuser()  # Get the current user's login name
    print(colored(f'WARNING: DEBUG IS ENABLED, NEVER RUN IN PRODUCTION! Running as {current_user}', 'magenta'))