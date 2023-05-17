import re

from django.contrib.auth.password_validation import MinimumLengthValidator as _MinimumLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_number_case(password):
    if not re.match(r'.*\d.*', password):
        raise ValidationError(
            _("This password must contain at least a number."),
            code='password_entirely_numeric',
        )


def validate_lower_case(password):
    if not re.match(r'.*[a-z].*', password):
        raise ValidationError(
            _('This password must contain at least a lower case.'),
            code='password_need_lower_case'
        )


def validate_upper_case(password):
    if not re.match(r'.*[A-Z].*', password):
        raise ValidationError(
            _('This password must contain at least a upper case.'),
            code='password_need_upper_case'
        )


def validate_special_case(password):
    special_chars = list('!@#$%^&*()-_+=~,.?')
    for char in password:
        if char in special_chars:
            return
    raise ValidationError(
        _('Password must contain at least one special chars.'),
        code='password_need_special_chars',
    )


validators = list((
    validate_number_case,
    validate_lower_case,
    validate_upper_case,
    validate_special_case
))


class BasePasswordValidator:
    """
    1.密码长度限制：默认8位（范围：8-64）
    2.密码复杂度：默认 低 （范围：高、中、低）
    低：同时包含数字、大写字母、小写字母、特殊字符中的2种
    中：同时包含数字、大写字母、小写字母、特殊字符中的3种
    高：同时包含数字、大写字母、小写字母、特殊字符中的4种
    """
    required_kinds = None
    full_kinds = 4
    error_messages = _('Password must contain at least one char in %(required_kinds)s of the four kind of chars: '
                       'number, upper cases, lower cases and special chars.')
    code = 'unsatisfied_password'

    def validate(self, password, user=None):
        fail_times = 0
        for validator in validators:
            try:
                validator(password)
            except ValidationError:
                fail_times += 1
            if fail_times > (self.full_kinds - self.required_kinds):
                raise ValidationError(
                    self.error_messages,
                    params={'required_kinds': self.required_kinds},
                    code=self.code
                )

    def get_help_text(self):
        return self.error_messages % {'required_kinds': self.required_kinds}


class LowLevelPasswordValidator(BasePasswordValidator):
    required_kinds = 2


class MediumLevelPasswordValidator(BasePasswordValidator):
    required_kinds = 3


class HighLevelPasswordValidator(BasePasswordValidator):
    required_kinds = 4


class MinimumLengthValidator(_MinimumLengthValidator):

    def validate(self, password, user=None):
        from common.core.settings import project_settings
        self.min_length = project_settings.security.password_min_length
        super().validate(password, user=user)
