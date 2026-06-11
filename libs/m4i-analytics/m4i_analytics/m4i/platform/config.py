import imp
import os
import sys
from typing import Optional

"""
Configurable values
"""
M4I_BASE_URI = "https://www.models4insight.com/"
REPOSITORY_BASE_URI = M4I_BASE_URI + "RestApi2/api/"
# uncomment and set IP address and port of your proxy server
# HTTP_PROXY = "http://IP:8080"
# HTTPS_PROXY ="http://IP:8080"

# set this setting to False in case you want the http connections
# NOT to use any proxy settings.
USE_DEFAULT_PROXIES = True

CONFIG_PATH_ENV_VAR = "M4I_PLATFORM_CONFIG"

HTTP_PROXY: Optional[str] = None
HTTPS_PROXY: Optional[str] = None

try:
    if CONFIG_PATH_ENV_VAR in os.environ:
        print(f"Loaded your LOCAL configuration at [{os.environ[CONFIG_PATH_ENV_VAR]}]")
        module = sys.modules[__name__]
        override_conf = imp.load_source("m4i_platform_config", os.environ[CONFIG_PATH_ENV_VAR])
        for key in dir(override_conf):
            if key.isupper():
                setattr(module, key, getattr(override_conf, key))

    else:
        import m4i_platform_config

        HTTP_PROXY = getattr(m4i_platform_config, "HTTP_PROXY", None)
        HTTPS_PROXY = getattr(m4i_platform_config, "HTTPS_PROXY", None)

        print(f"Loaded your LOCAL configuration at [{m4i_platform_config.__file__}]")
except ImportError:
    pass

"""
Dependent values
"""
RETRIEVE_MODEL_ENDPOINT = REPOSITORY_BASE_URI + "model/retrieve"
COMMIT_MODEL_ENDPOINT = REPOSITORY_BASE_URI + "model/v2/commit"
QUERY_MODEL_ENDPOINT = REPOSITORY_BASE_URI + "model/v2/query"
MODEL_PROVENANCE_ENDPOINT = REPOSITORY_BASE_URI + "project/provenance"
CLONE_BRANCH_ENDPOINT = REPOSITORY_BASE_URI + "branch/clone"
COMMIT_BRANCH_ENDPOINT = REPOSITORY_BASE_URI + "branch/commit"
FORCE_COMMIT_MODEL_ENDPOINT = REPOSITORY_BASE_URI + "model/v2/force"
DATA_UPLOAD_ENDPOINT = REPOSITORY_BASE_URI + "data"
DATA_RETRIEVE_ENDPOINT = REPOSITORY_BASE_URI + "data"
PROJECT_DETAILS_ENDPOINT = REPOSITORY_BASE_URI + "project/"
EXEMPTIONS_ENDPOINT = REPOSITORY_BASE_URI + "exempt/"

PROJECTS_BASE_URI = M4I_BASE_URI + "api/"
PROJECTS_LIST_ENDPOINT = M4I_BASE_URI + "projects/"

PROXIES: "dict[str, str]" = {}
if HTTP_PROXY and len(HTTP_PROXY) > 4:
    PROXIES["http"] = HTTP_PROXY
if HTTPS_PROXY and len(HTTPS_PROXY) > 4:
    PROXIES["https"] = HTTPS_PROXY


print("Connected to the M4I repository @ " + REPOSITORY_BASE_URI)
