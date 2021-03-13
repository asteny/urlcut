try:
    from .version import __version__, version_info
except ImportError:
    version_info = (0, 0, 0, "commit_hash")
    __version__ = "{}.{}.{}".format(*version_info)


authors = (("Pavel Sofrony", "pavel@sofrony.ru"),)

authors_email = ", ".join("{}".format(email) for _, email in authors)

__license__ = ("MIT",)
__author__ = ", ".join(
    "{} <{}>".format(name, email) for name, email in authors
)

package_info = (
    "Urlcut - yet another URL shortener built on asynchronous Python"
)

# It's same persons right now
__maintainer__ = __author__

__all__ = (
    "__author__",
    "__author__",
    "__license__",
    "__maintainer__",
    "__version__",
    "version_info",
)
