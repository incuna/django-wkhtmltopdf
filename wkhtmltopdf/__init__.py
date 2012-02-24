import os
if 'DJANGO_SETTINGS_MODULE' in os.environ:
    from .utils import *

__version__ = (0, 2)
def get_version():
    return '.'.join(map(str, __version__))
