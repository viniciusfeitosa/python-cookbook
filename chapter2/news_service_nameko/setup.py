#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='news_service_nameko',
    version='0.0.1',
    description='News service using Nameko',
    packages=find_packages(exclude=['test', 'test.*']),
    package_dir={'news_service_nameko': 'src'},
    zip_safe=True
)
