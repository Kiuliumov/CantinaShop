import pytest
from django.core.exceptions import ValidationError

from accounts.validators import NoProfanityValidator, PhoneNumberValidator, split_to_words


class TestPhoneNumberValidator:
    @pytest.mark.parametrize("value", ["", "+1234567890", "1234567"])
    def test__validate_valid_number__accepts(self, value):
        assert PhoneNumberValidator()(value) is None

    @pytest.mark.parametrize("value", ["123", "123-4567", "++123456789", "1" * 16])
    def test__validate_invalid_number__raises_validation_error(self, value):
        with pytest.raises(ValidationError, match="Phone number"):
            PhoneNumberValidator()(value)


class TestProfanityValidator:
    def test__split_to_words__separates_camel_case_and_digits(self):
        assert split_to_words("HelloWorld123") == ["Hello", "World", "123"]

    def test__validate_profanity__raises_validation_error(self):
        with pytest.raises(ValidationError, match="Inappropriate"):
            NoProfanityValidator()("shit")
