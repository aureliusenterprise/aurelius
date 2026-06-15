import importlib.util
import os
import sys

# Don't forget to add a trailing / after the server url
KEYCLOAK_JSON = {
    "realm": "m4i",
    "auth-server-url": "https://www.models4insight.com/auth/",
    "ssl-required": "external",
    "resource": "m4i_public",
    "public-client": True,
    "confidential-port": 0,
}

CONFIG_PATH_ENV_VAR = "M4I_KEYCLOAK_CONFIG"

try:
    if CONFIG_PATH_ENV_VAR in os.environ:
        print(f"Loaded your LOCAL configuration at [{os.environ[CONFIG_PATH_ENV_VAR]}]")
        module = sys.modules[__name__]
        spec = importlib.util.spec_from_file_location("m4i_keycloak_config", os.environ[CONFIG_PATH_ENV_VAR])
        override_conf = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(override_conf)  # type: ignore
        for key in dir(override_conf):
            if key.isupper():
                setattr(module, key, getattr(override_conf, key))

    else:
        import m4i_keycloak_config

        print(f"Loaded your LOCAL configuration at [{m4i_keycloak_config.__file__}]")
except ImportError:
    pass
