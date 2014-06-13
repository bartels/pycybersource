#!/usr/bin/env python
"""
A light wrapper for Cybersource SOAP Toolkit API
"""
from setuptools import setup
import pycybersource

setup(
    name='pycybersource',
    version=pycybersource.__version__,
    description='A light wrapper for Cybersource SOAP Toolkit API',
    author='Eric Bartels',
    author_email='ebartels@gmail.com',
    url='',
    packages=['pycybersource'],
    package_dir={'pycybersource': 'pycybersource'},
    platforms=['Platform Independent'],
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='cybersource payment soap suds api wrapper',
    requires=['suds'],
    install_requires=['suds'],
    test_suite='pycybersource.tests',
)
