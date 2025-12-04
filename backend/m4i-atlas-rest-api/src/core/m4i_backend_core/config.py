import imp
import os
import sys

"""
This file contains all the configuation parameters used by the application
"""

CONFIG_PATH_ENV_VAR = 'M4I_BACKEND_CONFIG'

# Authentication
AUTH_ISSUER = 'http://localhost:8180/auth/realms/m4i'
# PUBLIC KEY HEADER AND FOOTER ARE PART OF THE REQUIRED FORMAT. REPLACE ONLY THE KEY STRING.
AUTH_PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\n' \
                  'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAgxjFy7eKHkhV2IP3LOcgUhQOm3KFn/yKiQQj+hZJmqqDgvArlFDMkc3mdJmcec0BCAz45x17ZhJU6leHX1dFR272COIQHvga+8d6p5joTzc063Zi/Wkt+jb5Q4cQNpR1yGdQX0U6eYck5uWpYxK740HRYF+HRB6Uh9hZqkGWF6cKFs3XLwWUS/bbUrLSLzjXTDD2TxdjlnPXqluO26f0hTJkjL/BNC8QSrMBTqOqGAUgU71fVkUolwGkvCsOl0ZcEAZnhIXKYfvODTkI8hj8UVNQH4AECO4QhpoXwHDJl6t5Lb+Tr0d3aHind3GhmJQAyQ+QMGEtdsK5kPkXsPIu6wIDAQAB' \
                  '\n-----END PUBLIC KEY-----'


# Override the config by setting the "M4I_BACKEND_CONFIG" environment variable, or by providing m4i_backend_config.py at your pythonpath
try:
    if CONFIG_PATH_ENV_VAR in os.environ:
        print('Loaded your LOCAL configuration at [{}]'.format(
            os.environ[CONFIG_PATH_ENV_VAR]))
        module = sys.modules[__name__]
        override_conf = imp.load_source(
            'm4i_backend_config',
            os.environ[CONFIG_PATH_ENV_VAR])
        for key in dir(override_conf):
            if key.isupper():
                setattr(module, key, getattr(override_conf, key))

    else:
        from m4i_backend_config import *
        import m4i_backend_config
        print('Loaded your LOCAL configuration at [{}]'.format(
            m4i_backend_config.__file__))
    # END IF
except ImportError:
    print(f'Did not find a LOCAL configuration for {CONFIG_PATH_ENV_VAR}')
# END try
