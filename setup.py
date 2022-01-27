# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='skinport',
    version='0.1.0',
    author='Martin Simon',
    author_email='me@martinsimon.me',
    description='A Python wrapper around the Skinport API.',
    keywords=['skinport', 'Counter Strike', 'CSGO', 'DOTA2',
                'Rust', 'Team Fortress 2', 'TF2', 'wrapper', 'api'],
    url='https://github.com/barnumbirr/skinport',
    download_url='https://github.com/barnumbirr/skinport/archive/refs/heads/master.zip',
    packages=['skinport'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['requests'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
)
