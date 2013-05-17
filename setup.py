#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='reddit_meatspace',
    description='reddit meetup tools',
    version='0.1',
    author='Neil Williams',  # "meatspace" was written by a vegetarian
    author_email='neil@reddit.com',
    packages=find_packages(),
    install_requires=[
        'r2',
    ],
    entry_points={
        'r2.plugin':
            ['meatspace = reddit_meatspace:Meatspace']
    },
    zip_safe=False,
)
