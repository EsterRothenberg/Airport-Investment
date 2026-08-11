import pytest

from agent.tools import _validate_airport_code


class TestAirportCodeValidation:
    def test_valid_uppercase_code(self):
        _validate_airport_code("LAX")

    def test_valid_lowercase_code(self):
        _validate_airport_code("lax")

    def test_valid_code_with_whitespace(self):
        _validate_airport_code(" LAX ")

    def test_valid_mixed_case_code(self):
        _validate_airport_code("LaX")

    def test_invalid_two_letter_code(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code("LA")

    def test_invalid_four_letter_code(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code("LAXX")

    def test_invalid_numeric_code(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code("12!")

    def test_invalid_all_digits(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code("123")

    def test_invalid_mixed_alphanumeric(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code("LA1")

    def test_invalid_special_characters(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code("LA!")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code("")

    def test_whitespace_only(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code("   ")

    def test_none_input_empty_string(self):
        with pytest.raises(ValueError, match="3-letter IATA code"):
            _validate_airport_code(None)
