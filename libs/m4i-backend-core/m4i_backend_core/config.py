import os

"""
This file contains all the configuation parameters used by the application
"""

CONFIG_PATH_ENV_VAR = 'M4I_BACKEND_CONFIG'

AUTH_ISSUER = os.getenv('AUTH_ISSUER')
AUTH_PUBLIC_KEY = os.getenv('AUTH_PUBLIC_KEY')
