import pytest

from fhirbuild.help import letter_index_value

def test_valid_letter_index_value():
    assert letter_index_value('A') == 1
    assert letter_index_value('B') == 2
    assert letter_index_value('Z') == 26
    assert letter_index_value('a') == 1
    assert letter_index_value('b') == 2
    assert letter_index_value('z') == 26

def test_invalid_letter_index_value():
    with pytest.raises(ValueError):
        letter_index_value('1')