import os
from setuptools import setup, find_packages
import unittest

def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


with open('embarc_tools/version.py', 'r') as f:
    exec(f.read())

setup(
    name='embarc_cli',
    version=__version__,
    description='This is a command line tool for embarc open source platform',
    long_description_content_type='text/markdown',
    author='Jingru Wang',
    author_email='jingru@synopsys.com',
    keywords="embARC",
    url="https://github.com/foss-for-synopsys-dwc-arc-processors/embarc_tools",
    download_url='https://github.com/foss-for-synopsys-dwc-arc-processors/embarc_tools.git',
    packages=find_packages(),
    test_suite="setup.my_test_suite",
    entry_points={
        'console_scripts': [
            "embarc=embarc_tools.main:main",
        ]
    },
    python_requires='>=2.7.10,!=3.0.*,!=3.1.*,<4',
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'PyYAML',
        'colorama',
        'PrettyTable',
        'Jinja2',
        'beautifulsoup4',
        'GitPython',
        'pyelftools'
    ],

    include_package_data = True,
)
