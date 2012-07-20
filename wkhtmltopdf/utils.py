from __future__ import absolute_import

from itertools import chain
from os import fdopen
import sys
from tempfile import mkstemp

from django.conf import settings
from django.template import loader
from django.utils.encoding import smart_str

from .subprocess import check_output

WKHTMLTOPDF_CMD = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')


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
    options = {
        'quiet': True,
    }
    options.update(kwargs)

    args = list(chain([WKHTMLTOPDF_CMD],
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

