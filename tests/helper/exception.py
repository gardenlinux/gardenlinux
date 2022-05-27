class NotPartOfFeatureError(Exception):
    """Custom exception to throw when a test is called that is not in a feature
    that was used to build the gardenlinux image.
    """
    pass

class TestFailed(Exception):
    """Custom exception to throw when a test has failed."""
    pass

class DisabledBy(Exception):
    """Custom exception to throw when a test is explicitly disabled."""
    pass