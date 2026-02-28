"""
rewordapp.config
----------------

This module centralizes configuration settings and constants for RewordApp CE.
"""

from os import path
import yaml

from rewordapp.libs.common import dedent_and_strip

__version__ = '0.3.2'
version = __version__

__all__ = [
    'version',
]

# main app
main_app_text = f'RewordApp v{version} CE'

# packages
pyyaml_text = f"pyyaml v{yaml.__version__}"
pyyaml_link = "https://pypi.org/project/PyYAML/"

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
license_text = dedent_and_strip(
    """
    BSD 3-Clause License

    Copyright (c) 2021-2040, Geeks Trident LLC
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
)


def get_dependency():
    """Return a dictionary of package dependencies with names and PyPI links."""
    dependencies = dict(
        pyyaml=dict(package=pyyaml_text, url=pyyaml_link),
    )
    return dependencies

