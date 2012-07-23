from __future__ import absolute_import

from copy import copy
from itertools import chain
from os import fdopen
import sys
from tempfile import mkstemp

from django.conf import settings
from django.template import loader
from django.utils.encoding import smart_str

from .subprocess import check_output


def _options_to_args(**options):
    """Converts ``options`` into a string of command-line arguments."""
    flags = []
    for name in sorted(options):
        value = options[name]
        flags.append('--' + name.replace('_', '-'))
        if value is not True:
            flags.append(unicode(value))
    return flags


def wkhtmltopdf(pages, output=None, **kwargs):
    """
    Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.

    pages: List of file paths or URLs of the html to be converted.
    output: Optional output file path. If None, the output is returned.
    **kwargs: Passed to wkhtmltopdf via _extra_args() (See
              https://github.com/antialize/wkhtmltopdf/blob/master/README_WKHTMLTOPDF
              for acceptable args.)
              Kwargs is passed through as arguments. e.g.:
                  {'footer_html': 'http://example.com/foot.html'}
              becomes
                  '--footer-html http://example.com/foot.html'
              Where there is no value passed, use True. e.g.:
                  {'disable_javascript': True}
              becomes:
                  '--disable-javascript'

    example usage:
        wkhtmltopdf(pages=['/tmp/example.html'],
                    dpi=300,
                    orientation='Landscape',
                    disable_javascript=True)
    """
    if isinstance(pages, basestring):
        # Support a single page.
        pages = [pages]

    if output is None:
        # Standard output.
        output = '-'

    # Default options:
    options = getattr(settings, 'WKHTMLTOPDF_CMD_OPTIONS', None)
    if options is None:
        options = {'quiet': True}
    else:
        options = copy(options)
    options.update(kwargs)

    cmd = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')
    args = list(chain([cmd],
                      _options_to_args(**options),
                      list(pages),
                      [output]))
    return check_output(args, stderr=sys.stderr)


def template_to_temp_file(template_name, dictionary=None, context_instance=None):
    """
    Renders a template to a temp file, and returns the path of the file.
    """
    file_descriptor, tempfile_path = mkstemp(suffix='.html')
    with fdopen(file_descriptor, 'wt') as f:
        f.write(smart_str(loader.render_to_string(template_name, dictionary=dictionary, context_instance=context_instance)))
    return tempfile_path


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
    return '"{!s}"'.format(string.replace('\\', '\\\\').replace('"', '\\"'))
