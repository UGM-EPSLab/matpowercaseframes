from setuptools import setup, find_packages
import re
import os

with open("README.md", "r") as f:
    long_description = f.read()

PACKAGE_NAME = 'matpowercaseframes'
current_path = os.path.abspath(os.path.dirname(__file__))
version_line = open(os.path.join(current_path, PACKAGE_NAME, 'version.py'), "rt").read()

m = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_line, re.M)
__version__ = m.group(1)

setup(
    name = PACKAGE_NAME,
    version = __version__,
    description = "Parse MATPOWER case into pandas DataFrame",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = "Muhammad Yasirroni",
    author_email = "muhammadyasirroni@gmail.com",
    url = "https://github.com/UGM-EPSLab/MATPOWER-Case-Frames",
    packages = find_packages(),
    license = "MIT license",
    keywords = "psst",
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires = '>3.6',
    install_requires = [
        "pandas>=1.2.0",
        "numpy>=1.12"
        ],
    extras_require = {
        "matpower": [
            "matpower"
        ]
    },
    test_suite = "tests",
)
