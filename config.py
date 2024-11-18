import importlib

def get_config(config_name):
    try:
        config_module = importlib.import_module(f'.{config_name}', package=__name__)
        return getattr(config_module, f'{config_name.capitalize()}Config')
    except (ModuleNotFoundError, AttributeError):
        from .default import DefaultConfig
        return DefaultConfig
