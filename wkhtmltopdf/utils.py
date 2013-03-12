from __future__ import absolute_import

from copy import copy
from functools import wraps
from itertools import chain
import os
import re
import sys
import urllib
import urlparse
from warnings import warn

from django.conf import settings

from .subprocess import check_output


has_scheme = re.compile(r'^[^:/]+://')


# DEPRECATED: Remove when WKHTMLTOPDF_CMD_OPTIONS support is removed.
def _options_to_args(**options):
    """Converts ``options`` into a list of command-line arguments."""
    warn('_options_to-args() is deprecated', DeprecationWarning)
    flags = []
    for name in sorted(options):
        value = options[name]
        if value is None:
            continue
        flags.append('--' + name.replace('_', '-'))
        if value is not True:
            flags.append(unicode(value))
    return flags


def wkhtmltopdf(pages, output=None, cmd_args=None, **kwargs):
    """
    Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.

    pages: List of file paths or URLs of the html to be converted.
    output: Optional output file path. If None, the output is returned.
    cmd_args: List of additional command-line arguments for wkhtmltopdf.
              (See
              https://github.com/antialize/wkhtmltopdf/blob/master/README_WKHTMLTOPDF
              for acceptable args.)

    example usage:
        wkhtmltopdf(pages=['/tmp/example.html'],
                    cmd_args=['--dpi', '300',
                              '--orientation', 'Landscape',
                              '--disable-javascript']
    """
    if cmd_args is not None and kwargs:
        raise ValueError('Cannot mix cmd_args and **kwargs. '
                         '**kwargs is deprecated, use cmd_args instead.')

    if isinstance(pages, basestring):
        # Support a single page.
        pages = [pages]

    if output is None:
        # Standard output.
        output = '-'

    cmd_args = list(cmd_args) if cmd_args is not None else []

    # Default arguments:
    cmd_args = getattr(settings, 'WKHTMLTOPDF_CMD_ARGS', ['--quiet']) + cmd_args

    # Parse out deprecated settings variable and arguments
    if kwargs:
        warn('Call wkhtmltopdf with cmd_args instead of calling with **kwargs',
             RuntimeWarning, 2)
        return

    options = getattr(settings, 'WKHTMLTOPDF_CMD_OPTIONS', None)
    if options is not None:
        warn('Set WKHTMLTOPDF_CMD_ARGS instead of WKHTMLTOPDF_CMD_OPTIONS',
             RuntimeWarning)
        for k, v in options:
            kwargs.setdefault(k, v)
    if kwargs:
        cmd_args.extend(_options_to_args(**kwargs))

    # Force --encoding utf8 unless the user has explicitly overridden this.
    if '--encoding' not in cmd_args:
        cmd_args.extend(['--encoding', 'utf8'])

    env = getattr(settings, 'WKHTMLTOPDF_ENV', None)
    if env is not None:
        env = dict(os.environ, **env)

    cmd = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')
    args = list(chain([cmd],
                      cmd_args,
                      list(pages),
                      [output]))
    return check_output(args, stderr=sys.stderr, env=env)


def content_disposition_filename(filename):
    """
    Sanitize a file name to be used in the Content-Disposition HTTP
    header.

    Even if the standard is quite permissive in terms of
    characters, there are a lot of edge cases that are not supported by
    different browsers.

    See http://greenbytes.de/tech/tc2231/#attmultinstances for more details.
    """
    filename = filename.replace(';', '').replace('"', '')
    return http_quote(filename)


def http_quote(string):
    """
    Given a unicode string, will do its dandiest to give you back a
    valid ascii charset string you can use in, say, http headers and the
    like.
    """
    if isinstance(string, unicode):
        try:
            import unidecode
            string = unidecode.unidecode(string)
        except ImportError:
            string = string.encode('ascii', 'replace')
    # Wrap in double-quotes for ; , and the like
    return '"{0!s}"'.format(string.replace('\\', '\\\\').replace('"', '\\"'))


def pathname2fileurl(pathname, ignore_url=True):
    """Returns a file:// URL for pathname. Handles OS-specific conversions.

    If ignore_url, any pathnames with a scheme:// prefix will not be
    modified.
    """
    if not pathname:
        raise ValueError('Invalid pathname: {0!r}'.format(pathname))

    is_url = has_scheme.match(pathname)
    if ignore_url and is_url:
        return pathname         # Not a real pathname

    if is_url:
        normpath = pathname
    else:
        # Normalize pathnames by removing junk characters
        normpath = os.path.normpath(pathname)

        # Ensure directories end with a single slash
        if (pathname.endswith('/') or os.path.isdir(normpath)) and \
           not normpath.endswith('/'):
            normpath += '/'

    return urlparse.urljoin('file:',
                            urllib.pathname2url(normpath.encode('utf-8')))


try:
    # From Django 1.4 and up
    from django.test.utils import override_settings
except ImportError:
    # Copied from Django 1.4 for use in Django 1.3. Remove when Django 1.3 is
    # deprecated for this package.
    class override_settings(object):
        """
        Acts as either a decorator, or a context manager. If it's a decorator it
        takes a function and returns a wrapped function. If it's a contextmanager
        it's used with the ``with`` statement. In either event entering/exiting
        are called before and after, respectively, the function/block is executed.
        """
        def __init__(self, **kwargs):
            self.options = kwargs
            self.wrapped = settings._wrapped

        def __enter__(self):
            self.enable()

        def __exit__(self, exc_type, exc_value, traceback):
            self.disable()

        def __call__(self, test_func):
            from django.test import TransactionTestCase
            if isinstance(test_func, type) and issubclass(test_func, TransactionTestCase):
                original_pre_setup = test_func._pre_setup
                original_post_teardown = test_func._post_teardown
                def _pre_setup(innerself):
                    self.enable()
                    original_pre_setup(innerself)
                def _post_teardown(innerself):
                    original_post_teardown(innerself)
                    self.disable()
                test_func._pre_setup = _pre_setup
                test_func._post_teardown = _post_teardown
                return test_func
            else:
                @wraps(test_func)
                def inner(*args, **kwargs):
                    with self:
                        return test_func(*args, **kwargs)
            return inner

        def enable(self):
            override = copy(settings._wrapped)
            for key, new_value in self.options.items():
                setattr(override, key, new_value)
            settings._wrapped = override

        def disable(self):
            settings._wrapped = self.wrapped
