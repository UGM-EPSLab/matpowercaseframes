from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name = "matpowercaseframes",
    version = "0.0.1a0",
    description = "Parse MATPOWER case into pandas DataFrame",
    long_description = readme,
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
