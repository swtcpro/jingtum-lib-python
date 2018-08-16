#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

setup(
     name="jingtum_python_lib",
     version="1.1.0",
     author="wuhan python dev team",
     author_email="caizl2002@hotmail.com",
     description=("jingtum_lib to be used for interacting with jingtum blockchain network"),
     license="MIT",
     keywords=["jingtum", "lib", "python"],
     url="https://github.com/swtcpro/jingtum-lib-python",
     packages=['jingtum_python_lib', 'jingtum_python_baselib'],
     include_package_data=True,

     install_requires=[
         'ecdsa >= 0.13',
         'eventemitter >= 0.2.0',
         'schedule >= 0.5.0',
         'six >= 1.11.0',
         'websocket-client >= 0.47.0'
     ],

     #long_description=open('README.md').read,
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     zip_safe=False
)