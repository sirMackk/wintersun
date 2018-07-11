class WintersunException(Exception):
    """General Wintersun exception"""


class IncompletePost(WintersunException):
    """Post is missing data"""


class PostRepoException(WintersunException):
    """Error with Post Repository"""


class NotFound(PostRepoException):
    """Post not found in Repository"""


class DuplicatePost(PostRepoException):
    """Duplicate Post in Repository"""
