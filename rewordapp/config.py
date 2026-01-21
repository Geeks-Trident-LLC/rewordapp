"""
rewordapp.config
----------------

This module centralizes configuration settings and constants for RewordApp CE.
"""

from os import path

from rewordapp.deps import genericlib_file_module as file
from rewordapp.deps import genericlib_version
from rewordapp.deps import regexapp_version

__version__ = '0.1.0a1'
version = __version__

__all__ = [
    'version',
    'Data'
]


class Data:
    """Centralized application metadata, package info, and license details for RewordApp CE."""

    # main app
    main_app_text = f'RewordApp v{version} CE'

    # packages
    genericlib_text = f"genericlib v{genericlib_version}"
    genericlib_link = "https://pypi.org/project/genericlib/"

    regexapp_text = 'regexapp v{}'.format(regexapp_version)
    regexapp_link = 'https://pypi.org/project/regexapp'

    # company
    company = 'Geeks Trident LLC'
    company_url = 'https://www.geekstrident.com/'

    # URL
    repo_url = 'https://github.com/Geeks-Trident-LLC/rewordapp'
    documentation_url = path.join(repo_url, 'blob/develop/README.md')
    license_url = path.join(repo_url, 'blob/develop/LICENSE')

    # License
    years = '2021-2040'
    license_name = 'RewordApp License'
    copyright_text = 'Copyright @ {}'.format(years)
    license = file.read('LICENSE')

    @classmethod
    def get_dependency(cls):
        """Return a dictionary of package dependencies with names and PyPI links."""
        dependencies = dict(
            genericlib=dict(
                package=cls.genericlib_text,
                url=cls.genericlib_link
            ),
            regexapp=dict(
                package=cls.regexapp_text,
                url=cls.regexapp_link
            )
        )
        return dependencies
