#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='wxwork_api',
    version=0.1,
    description='企业微信API',
    long_description= '''
企业微信API，
参考 https://github.com/sbzhu/weworkapi_python的二次封装
    ''' ,
    author='RStudio',
    author_email='rain.wen@outlook.com',
    packages=find_packages(),
    install_requires=[

    ],
    python_requires='>=3.6',
    extras_require={

    },
    tests_require=[

    ],
)

