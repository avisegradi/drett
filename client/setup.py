#!/usr/bin/env -e python

import setuptools
from pip.req import parse_requirements

setuptools.setup(
    name='drett-client',
    version='0.1.0',
    author='Adam Visegradi',
    author_email='a.visegradi@gmail.com',
    namespace_packages=[
        'drett',
    ],
    packages=[
        'drett.client',
    ],
    scripts=[
        'drett-client-test',
    ],
    url='https://github.com/avisegradi/drett',
    license='LICENSE.txt',
    description='Distributed Resource Tracking',
    long_description=open('README.txt').read(),
    install_requires=[
        'argparse',
        'pymongo',
        'PyYAML',
        'requests',
    ],
)
