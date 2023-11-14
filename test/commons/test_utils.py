from buzz_el.commons.utils import is_valid_url


def test_valid_uri():
    uri_to_test = "http://www.example.com/resource"
    assert is_valid_url(uri_to_test) is True


def test_invalid_uri():
    uri_to_test = "rdfs:label"
    assert is_valid_url(uri_to_test) is False


def test_another_valid_uri():
    uri_to_test = "https://rdf.example.org/data"
    assert is_valid_url(uri_to_test) is True


def test_empty_string():
    uri_to_test = ""
    assert is_valid_url(uri_to_test) is False


def test_none_input():
    uri_to_test = None
    assert is_valid_url(uri_to_test) is False


def test_invalid_uri_special_characters():
    uri_to_test = "http://www.example.com/resource#frag^ment"
    assert is_valid_url(uri_to_test) is True


def test_valid_uri_with_unicode_characters():
    uri_to_test = "http://www.example.com/caf%C3%A9"
    assert is_valid_url(uri_to_test) is True
