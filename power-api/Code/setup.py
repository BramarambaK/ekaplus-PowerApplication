# -*- coding: utf-8 -*-

# Learn more: https://github.com/ekaplus/power/valuation

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='valuation',
    version='0.1.0',
    description='Valuation service',
    long_description=readme,
    author='Srinivasan Murugesan',
    author_email='srinivasan.murugesan@ekaplus.com',
    url='https://github.com/ekaplus/power/valuation',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)