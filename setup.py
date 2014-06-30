#!/usr/bin/env python
"""
Setup script
"""

from setuptools import setup
from repo_manager import __version__

setup(
    name='repo_manager',
    description='A simple application to manage RPM repositories',
    version=__version__,
    author='Pierre-Yves Chibon',
    author_email='pingou@pingoured.fr',
    maintainer='Pierre-Yves Chibon',
    maintainer_email='pingou@pingoured.fr',
    license='GPLv3+',
    url='https://github.com/pypingou/repo_manager',
    entry_points="""
    [console_scripts]
        repo_manager = repo_manager:main
    """,
    packages=['repo_manager'],
    test_suite="tests",
)
