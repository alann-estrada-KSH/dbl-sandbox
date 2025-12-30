#!/usr/bin/env python3
"""
DBL - Database Layering
Setup configuration
"""

from setuptools import setup, find_packages
import os

# Read version from constants
version = "0.0.1-alpha"
try:
    from dbl.constants import VERSION
    version = VERSION
except ImportError:
    pass

# Read long description from README
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="dbl-sandbox",
    version=version,
    description="Git-like version control for databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alan Estrada",
    author_email="",
    url="https://github.com/alann-estrada-KSH/dbl-sandbox",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "dbl=dbl.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "Topic :: Database",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords="database version-control migrations git schema postgresql mysql",
    project_urls={
        "Documentation": "https://alann-estrada-ksh.github.io/dbl-sandbox/",
        "Source": "https://github.com/alann-estrada-KSH/dbl-sandbox",
        "Issues": "https://github.com/alann-estrada-KSH/dbl-sandbox/issues",
    },
)
