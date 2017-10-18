from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import MinimumLengthValidator
from django.contrib.auth.password_validation import NumericPasswordValidator
from django.utils.translation import gettext as _


class MinLengthValidator(MinimumLengthValidator):
    def __init__(self, min_length):
        super(MinLengthValidator, self).__init__(min_length)

    def get_help_text(self):
        return _(
            "Be longer than {0}".format(self.min_length)
        )

class NumericPasswordValidator(NumericPasswordValidator):
    def __init__(self):
        super(NumericPasswordValidator, self).__init__()

    def get_help_text(self):
        return _(
            "Have at least 1 letter"
        )

class SpecialCharacterValidator:
    """
    Password validator to ensure that passwords contain one or more in a list
    of characters

    """

    def __init__(self, special_characters=('!','@','#')):
        self.special_characters = special_characters

    def validate(self, password, user=None):
        res = set(password) & set(self.special_characters)
        if len(res) == 0:
            raise ValidationError(
                _("Your password must contain at least one of the following: {0}".format(self.special_characters)),
                code='missing special characters',
                params={'special_characters': self.special_characters},
            )

    def get_help_text(self):
        return _(
            "Have at least 1 of: {0}".format(self.special_characters)
        )


class HasNumericCharacterValidator:
    """
    Password validator to ensure that passwords contain number

    """

    def validate(self, password, user=None):
        res = filter(lambda x: x.isdigit() == True, password)
        if len(res) == 0:
            raise ValidationError(
                _("Your password must contain at least one number"),
                code='missing number',
            )

    def get_help_text(self):
        return _(
            "Have at least 1 number"
        )


class HasUpperAndLowerCaseValidator:
    """
    Password validator to ensure that passwords contain both upper and lower
    characters

    """

    def validate(self, password, user=None):
        res = filter(lambda x: x.isupper() == True, password)
        if len(res) == 0 or len(res) == len(password):
            raise ValidationError(
                _("Your password must contain both upper and lower case letters"),
                code='case error',
            )

    def get_help_text(self):
        return _(
            "Have least 1 upper and lower case character"
        )
