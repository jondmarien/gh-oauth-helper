"""
Basic tests for the gh_oauth_helper package.
"""

from gh_oauth_helper import __version__, __author__, __description__


def test_version():
    """Test that version is defined and is a string."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_author():
    """Test that author is defined and is a string."""
    assert isinstance(__author__, str)
    assert len(__author__) > 0


def test_description():
    """Test that description is defined and is a string."""
    assert isinstance(__description__, str)
    assert len(__description__) > 0


def test_package_import():
    """Test that the package can be imported successfully."""
    import gh_oauth_helper

    assert gh_oauth_helper is not None
