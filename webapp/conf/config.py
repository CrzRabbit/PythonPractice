# from PythonPractice.webapp.conf import config_default
from webapp.conf import config_default

configs = config_default.configs

def merge(default, override):
    for k, v in override.items():
        for k1, v1 in override[k].items():
            default[k][k1] = v1
    return default

try:
    from webapp.conf import config_override
    configs = merge(configs, config_override.configs)
except ImportError:
    pass