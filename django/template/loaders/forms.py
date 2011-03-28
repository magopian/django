"""
Wrapper for loading the default forms templates, located in
django/forms/templates.
"""

import os

from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.template.loader import BaseLoader
from django.utils._os import safe_join


class Loader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        forms_template_dir = os.path.join(os.path.dirname(__file__),
                                          os.pardir, os.pardir,
                                          'forms', 'templates')
        template_path = safe_join(forms_template_dir, template_name)

        try:
            template_file = open(template_path)
            try:
                content = template_file.read().decode(settings.FILE_CHARSET)
                return (content, template_path)
            finally:
                template_file.close()
        except IOError:
            pass
        raise TemplateDoesNotExist(template_name)
