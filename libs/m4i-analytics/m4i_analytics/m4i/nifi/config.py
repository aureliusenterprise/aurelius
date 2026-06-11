import imp
import os
import sys

NIFI_BASE_URI = "http://localhost:8282/nifi-api/"

FLOW_PROCESS_GROUPS_ENDPOINT = NIFI_BASE_URI + "flow/process-groups/"
PROCESSORS_ENDPOINT = NIFI_BASE_URI + "processors/"

CONFIG_PATH_ENV_VAR = "M4I_NIFI_CONFIG"

try:
    if CONFIG_PATH_ENV_VAR in os.environ:
        # Explicitly import config module that is not in pythonpath; useful
        # for case where app is being executed via pex.
        print(f"Loaded your LOCAL configuration at [{os.environ[CONFIG_PATH_ENV_VAR]}]")
        module = sys.modules[__name__]
        override_conf = imp.load_source("m4i_nifi_config", os.environ[CONFIG_PATH_ENV_VAR])
        for key in dir(override_conf):
            if key.isupper():
                setattr(module, key, getattr(override_conf, key))

    else:
        import m4i_nifi_config

        print(f"Loaded your LOCAL configuration at [{m4i_nifi_config.__file__}]")
except ImportError:
    pass
