import imp
import os
import sys

"""
Configurable values
"""
BASE_URI = "http://portal.models4insight.com/m4i/rest/"

TASK_ID_KEY = "taskid"
PROJECT_NAME_KEY = "project_name"
RUN_BY_KEY = "userid"

TABLENAME_KEY = "table_name"

USERNAME_KEY = "username"
FIRST_NAME_KEY = "first_name"
LAST_NAME_KEY = "last_name"
EMAIL_KEY = "email"

USERS_KEY = "users"

RM_USER_USERNAME_KEY = "username"

BRANCH_NAME_KEY = "branch_name"
VERSION_KEY = "version"

PARSER_NAME_KEY = "parser_name"

DELTA_REVISION_KEY = "delta_revision"
DATA_REVISION_KEY = "data_revision"

INSTANCEID_KEY = "instance_id"

SQLALCHEMY_URL = "mysql+pymysql://m4i:6sn$s(_mjHh=@localhost:3306/m4i"
DB_CONNECTION_LIFETIME = 10000

# uncomment and set IP address and port of your proxy server
# HTTP_PROXY = "http://IP:8080"
# HTTPS_PROXY ="http://IP:8080"

# set this setting to False in case you want the
# http connections NOT to use any proxy settings.
USE_DEFAULT_PROXIES = True

CONFIG_PATH_ENV_VAR = "M4I_PORTAL_CONFIG"

try:
    if CONFIG_PATH_ENV_VAR in os.environ:
        print(f"Loaded your LOCAL configuration at [{os.environ[CONFIG_PATH_ENV_VAR]}]")
        module = sys.modules[__name__]
        override_conf = imp.load_source("m4i_portal_config", os.environ[CONFIG_PATH_ENV_VAR])
        for key in dir(override_conf):
            if key.isupper():
                setattr(module, key, getattr(override_conf, key))

    else:
        import m4i_portal_config

        print(f"Loaded your LOCAL configuration at [{m4i_portal_config.__file__}]")
except ImportError:
    pass

"""
Dependent values
"""

DELTA_ENDPOINT = BASE_URI + "delta"
DELTA_ASYNC_ENDPOINT = DELTA_ENDPOINT + "/async"
DATA_ENDPOINT = BASE_URI + "data"
UPDATE_PROJECT_ENDPOINT = BASE_URI + "update"
CREATE_PROJECT_ENDPOINT = BASE_URI + "project/create"
UNPUBLISH_PROJECT_ENDPOINT = BASE_URI + "project/unpublish"
NEW_PROJECT_USER_ENDPOINT = BASE_URI + "project/newuser"
REMOVE_PROJECT_USER_ENDPOINT = BASE_URI + "project/removeuser"
TABLE_DASHBOARD_ENDPOINT = BASE_URI + "dashboards/table"
INSTANCEWORKFLOW_QUERY_ENDPOINT = BASE_URI + "instanceworkflow/query"

PROXIES = {}
_http_proxy = os.getenv("HTTP_PROXY", "")
_https_proxy = os.getenv("HTTPS_PROXY", "")
if len(_http_proxy) > 4:
    PROXIES["http"] = _http_proxy
if len(_https_proxy) > 4:
    PROXIES["https"] = _https_proxy

print("Connected to the M4I portal @ " + BASE_URI)
