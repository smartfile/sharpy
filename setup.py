#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError as err:
    from distutils.core import setup

from sharpy import VERSION

setup(
    name='Sharpy',
    version=".".join(map(str, VERSION)),
    description='Python client for the Cheddar Getter API (http://cheddargetter.com).',
    author="Sean O'Connor",
    author_email="sean@saaspire.com",
    url="https://github.com/Saaspire/sharpy",
    packages=['sharpy'],
    license="BSD",
    long_description=open('README.rst').read(),
    install_requires=['httplib2', 'citelementtree', 'python-dateutil'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
