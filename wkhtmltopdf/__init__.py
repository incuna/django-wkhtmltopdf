try:
    import os
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        from .utils import *  # noqa
except:
    pass

__author__ = 'Incuna Ltd'
__version__ = '3.0.0'
