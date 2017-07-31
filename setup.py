#!/usr/bin/env python
import os
from setuptools import setup, find_packages


BASE = os.path.dirname(__file__)
README_PATH = os.path.join(BASE, 'README.rst')
CHANGES_PATH = os.path.join(BASE, 'CHANGES.rst')
long_description = '\n\n'.join((
    open(README_PATH).read(),
    open(CHANGES_PATH).read(),
))


setup(
    name='django-mediawiki-auth',
    version='0.0.2',
    url='https://github.com/damoti/django-mediawiki-auth',
    license='BSD',
    description='Django uses MediaWiki session to seamlessly authenticate users.',
    long_description=long_description,
    author='Lex Berezhny',
    author_email='lex@damoti.com',
    keywords='django,mediawiki,wiki,wikipedia,php,session,auth',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=('mediawiki_auth.tests',)),
    install_requires=[
        'phpserialize',
    ],
    include_package_data=True
)
