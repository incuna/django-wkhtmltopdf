import os
try:
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        from .utils import *
except ImportError:
    pass

__author__ = 'Incuna Ltd'
__version__ = '3.0.0'
