#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

setup(
     name="jingtum_libs",
     version="1.0.3",
     author="wuhan python dev team",
     author_email="caizl2002@hotmail.com",
     description=("jingtum_lib to be used for interacting with jingtum blockchain network"),
     license="GPLv3",
     keywords="jingtum",
     url="https://github.com/swtcpro/jingtum-lib-python",
     packages=['jingtum_python_baselib', 'src','test', 'src.utils'],
     data_files=[('', ['requirements.txt', 'LICENSE', 'README.md']),
                 ('src', ['src/config.json'])],

     install_requires=[
         'ecdsa >= 0.13',
         'eventemitter >= 0.2.0',
         'schedule >= 0.5.0',
         'six >= 1.11.0',
         'websocket-client >= 0.47.0'
     ],

     #long_description=open('README.md').read,
     classifiers=[  # 程序的所属分类列表
         "Development Status :: 3 - Alpha",
         "Topic :: Utilities",
         "License :: OSI Approved :: GNU General Public License (GPL)",
     ],
     # 此项需要，否则卸载时报windows error
     zip_safe=False
)