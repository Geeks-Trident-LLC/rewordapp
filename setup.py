"""Packaging rewordapp for distribution, installation, integration, and seamless deployment."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rewordapp",
    version="0.1.0a2",  # pre-alpha versioning to signal alpha/beta status
    license="BSD-3-Clause",
    license_files=["LICENSE"],
    description="A versatile Python utility that transforms text into readable "
                "yet obfuscated form, designed for remote work and contract "
                "development scenarios. It helps safeguard data integrity and "
                "confidentiality by ensuring sensitive information remains "
                "protected while still maintaining usability for testing, "
                "automation, and collaborative workflows across diverse environments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tuyen Mathew Duong",
    author_email="tuyen@geekstrident.com",
    maintainer="Tuyen Mathew Duong",
    maintainer_email="tuyen@geekstrident.com",
    install_requires=[
        "genericlib",
        "regexapp",
        "pyyaml"
    ],
    url="https://github.com/Geeks-Trident-LLC/rewordapp",
    packages=find_packages(
        exclude=(
            "tests*", "testing*", "examples*",
            "build*", "dist*", "docs*", "venv*"
        )
    ),
    project_urls={
        "Documentation": "https://github.com/Geeks-Trident-LLC/rewordapp/wiki",
        "Source": "https://github.com/Geeks-Trident-LLC/rewordapp",
        "Tracker": "https://github.com/Geeks-Trident-LLC/rewordapp/issues",
    },
    python_requires=">=3.9",
    include_package_data=True,
    package_data={"": ["LICENSE", "README.md"]},
    entry_points={
        "console_scripts": [
            "rewordapp = rewordapp.main:execute",
            "rewordapp-gui = rewordapp.application:execute",
            "reword-app = rewordapp.application:execute",
        ]
    },
    classifiers=[
        # development status
        "Development Status :: 3 - Alpha",
        # natural language
        "Natural Language :: English",
        # intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        # operating system
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        # programming language
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        # topic
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing",
    ],
    keywords=(
        "text rewriter, text generator, text automation, "
        "phrase rephraser, language processing, NLP toolkit, "
        "Python text module, code generation, QA automation, "
        "software testing, text normalization, content transformation, "
        "data security, privacy protection, remote collaboration"
    ),
)
