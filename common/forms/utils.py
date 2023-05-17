from django.forms.utils import ErrorList as DjangoErrorList
from django.utils.html import html_safe, format_html_join


@html_safe
class ErrorList(DjangoErrorList):

    def __init__(self, initlist=None, error_class=None):
        super().__init__(initlist=initlist, error_class='alert alert-danger')

    def __str__(self):
        return self.as_div()

    def as_div(self):
        if not self.data:
            return ''
        return format_html_join(
            '\n', '<div class="%s" role="alert">{}</div>' % self.error_class, ((e,) for e in self),
        )
