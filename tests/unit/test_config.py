"""
Unit tests for the `rewordapp.config` module.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/test_config.py
    or
    $ python -m pytest tests/unit/test_config.py
"""


import pytest

from rewordapp import version
import rewordapp.config as config
from rewordapp.deps import genericlib_shell_module as shell

app_data = config.Data()


# Package info for regexapp
pkg_info = shell.PackageInfo("rewordapp")

# Skip marker if rewordapp is not installed
skip_if_missing_rewordapp = pytest.mark.skipif(
    not pkg_info.is_installed,
    reason="Skipping: rewordapp package is not installed."
)


@skip_if_missing_rewordapp
def test_version_matches_config():
    """Ensure installed package version matches config version."""
    assert pkg_info.is_installed is True
    assert pkg_info.version == config.version


class TestData:
    """Tests for Data class."""

    def test_main_app_text(self):
        """Check main app text."""
        assert f"v{version}" in app_data.main_app_text

    @pytest.mark.parametrize(
        "attr",
        [
            "regexapp",
            "genericlib",
        ],
    )
    def test_package_texts(self, attr):
        """Check package text strings."""
        expected = f"{attr} v"
        assert getattr(app_data, f"{attr}_text").lower().startswith(expected)

    @pytest.mark.parametrize(
        "attr",
        [
            "regexapp",
            "genericlib",
        ],
    )
    def test_package_links(self, attr):
        """Check package links."""
        expected = f"https://pypi.org/project/{attr}"
        assert getattr(app_data, f"{attr}_link").rstrip("/").lower() == expected

    def test_company_info(self):
        """Check company info."""
        assert app_data.company == "Geeks Trident LLC"
        assert "geekstrident.com" in app_data.company_url

    def test_repo_and_docs_urls(self):
        """Check repo and docs URLs."""
        assert app_data.repo_url.startswith("https://github.com/")
        assert app_data.documentation_url.endswith("README.md")
        assert app_data.license_url.endswith("LICENSE")

    def test_license_info(self):
        """Check license info."""
        assert "RewordApp License" in app_data.license_name
        assert "2021-2040" in app_data.copyright_text
        assert isinstance(app_data.license, str)

    @pytest.mark.parametrize(
        "pkg",
        [
            "regexapp",
            "genericlib",
        ],
    )
    def test_get_dependency(self, pkg):
        """Check dependency dict."""
        pkg_name, pkg_url = app_data.get_dependency().get(pkg).values()
        assert pkg_name.startswith(f"{pkg} v")
        assert pkg_url.rstrip("/").lower() == f"https://pypi.org/project/{pkg}"
