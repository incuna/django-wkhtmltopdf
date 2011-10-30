from os import fdopen
from subprocess import Popen, PIPE, CalledProcessError
from tempfile import mkstemp

from django.conf import settings
from django.template import loader
from django.utils.encoding import smart_str

WKHTMLTOPDF_CMD = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')

def wkhtmltopdf(pages, output=None, **kwargs):
    """
    Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.

    pages: List of file paths or URLs of the html to be converted.
    output: Optional output file path.
    **kwargs: Passed to wkhtmltopdf via _extra_args() (See
              https://github.com/antialize/wkhtmltopdf/blob/master/README_WKHTMLTOPDF
              for acceptable args.)
              Kwargs is passed through as arguments. e.g.:
                  {'footer_html': 'http://example.com/foot.html'}
              becomes
                  '--footer-html http://example.com/foot.html'
              Where there is no value passed, use a blank string. e.g.:
                  {'disable_javascript': ''}
              becomes:
                  '--disable-javascript '

    example usage:
        wkhtmltopdf(html_path="~/example.html",
                    dpi=300,
                    orientation="Landscape",
                    disable_javascript="")
    """

    def _extra_args(**kwargs):
        """Converts kwargs into a string of flags to be passed to wkhtmltopdf."""
        flags = ''
        for k, v in kwargs.items():
            flags += ' --%s %s' % (k.replace('_', '-'), v)
        return flags

    if not isinstance(pages, list):
        pages = [pages]

    kwargs['quiet'] = ''
    args = '%s %s %s %s' % (WKHTMLTOPDF_CMD, _extra_args(**kwargs), ' '.join(pages), output or '-')

    process = Popen(args, stdout=PIPE, shell=True)
    stdoutdata, stderrdata = process.communicate()

    if process.returncode != 0:
        raise CalledProcessError(process.returncode, args)

    if output is None:
        output = stdoutdata

    return output

def template_to_temp_file(*args, **kwargs):
    """
    Renders a template to a temp file, and returns the path of the file.
    """
    file_descriptor, tempfile_path = mkstemp(suffix='.html')
    with fdopen(file_descriptor, 'wt') as f:
        f.write(smart_str(loader.render_to_string(*args, **kwargs)))
    return tempfile_path

