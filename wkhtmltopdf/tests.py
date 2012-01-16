from django.test import TestCase

from utils import template_to_temp_file

class TestUtils(TestCase):
    def test_template_to_temp_file(self):
        """Should render a template to a temporary file."""
        title = 'A test template.'
        temp_file = template_to_temp_file('sample.html', {'title': title})
        with open(temp_file, 'r') as f:
            saved_content = f.read()
        self.assertTrue(title in saved_content)

