#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

# lib_name = 'wxworkapi'
setup(
    name='wxworkapi',
    py_modules=['wxworkapi'],
    version='2019.10',
    description='企业微信API',
    long_description='''
企业微信API，
参考 https://github.com/sbzhu/weworkapi_python的二次封装
    ''',
    author='RStudio',
    author_email='rain.wen@outlook.com',
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    #依赖包
    install_requires=[

    ],
    python_requires='>=3.6',
    #依赖的文件
    extras_require={

    },
    tests_require=[

    ],
)

