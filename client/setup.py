#!/usr/bin/env -e python

import setuptools
from pip.req import parse_requirements

reqs = [ str(i.req) for i in parse_requirements('requirements.txt') ]

setuptools.setup(
    name='drett-client',
    version='0.1.0',
    author='Adam Visegradi',
    author_email='a.visegradi@gmail.com',
    namespace_packages=['drett'],
    packages=['drett.client'],
    scripts=[],
    url='https://github.com/avisegradi/drett',
    license='LICENSE.txt',
    description='Distributed Resource Tracking',
    long_description=open('README.txt').read(),
    install_requires=reqs,
)
