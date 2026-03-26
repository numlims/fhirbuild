import pytest 
import fhirbuild.csvtofhir as ctf
import fhirbuild.help as fbh

def test_parse_valid_tube_positions():
    assert ctf.parse_tube_position("A01") == (1, 1)
    assert ctf.parse_tube_position("B02") == (2, 2)
    assert ctf.parse_tube_position("C03") == (3, 3)
    assert ctf.parse_tube_position("D10") == (10, 4)

def test_parse_invalid_tube_positions():
    with pytest.raises(ValueError):
        ctf.parse_tube_position("")   

    with pytest.raises(ValueError):
        ctf.parse_tube_position("AA1")   

    with pytest.raises(ValueError):
        ctf.parse_tube_position("1A")   

    