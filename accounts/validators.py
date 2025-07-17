from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from better_profanity import profanity
import re

profanity.load_censor_words()


def split_to_words(value):
    parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+|[0-9]+', value)
    return parts

@deconstructible
class NoProfanityValidator:
    message = "Inappropriate language is not allowed."
    code = "profanity"

    def __init__(self, message=None, code=None):
        profanity.load_censor_words()
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        parts = split_to_words(value)
        for part in parts:
            if profanity.contains_profanity(part.lower()):
                raise ValidationError(self.message, code=self.code)

@deconstructible
class PhoneNumberValidator:
    message = "Phone number must contain only digits and optional '+' at the start."
    code = "invalid_phone"

    def __init__(self, message=None, code=None):
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        if value and not re.fullmatch(r'^\+?\d{7,15}$', value):
            raise ValidationError(self.message, code=self.code)
