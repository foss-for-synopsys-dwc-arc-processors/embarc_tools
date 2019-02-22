import os

from setuptools import setup, find_packages

setup(
    name='embarc_cli',
    version='0.0.3',
    description='This is a tool for Embedded Development with embARC',
    author='Jingru',
    author_email='1961295051@qq.com',
    keywords="embARC",
    url="",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            "embarc=embarc_tools.main:main",
        ]
    },
    install_requires=[
        'PyYAML',
        'colorama',
        'PrettyTable',
        'Jinja2'
    ],

    include_package_data = True,
)
