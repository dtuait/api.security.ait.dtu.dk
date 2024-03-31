from .settings import *
from termcolor import colored

DEBUG = True

if DEBUG:
    print(colored('WARNING: DEBUG IS ENABLED, NEVER RUN IN PRODUCTION!', 'magenta'))