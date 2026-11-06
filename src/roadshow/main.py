"""Provide the Roadshow version command."""

from roadshow.version import get_version

__version__ = get_version()


def main() -> None:
    """Print the installed Roadshow version."""
    print(f"roadshow {__version__}")
