from urllib.parse import urlparse


def is_valid_url(uri):
    """Test if a string is a URL or not.

    Parameters
    ----------
    uri : str
        The string to test.

    Returns
    -------
    bool
        Whether the string is da URL.
    """
    try:
        result = urlparse(uri)
        # Check if the scheme component is present
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
