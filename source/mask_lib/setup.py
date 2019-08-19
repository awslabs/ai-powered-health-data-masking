# coding: utf-8

from setuptools import setup, find_packages
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    
setup(
    name='mask_lib',
    version='1.0',
    description='Library for masking sensitive health information using AWS AI services',
    author='AWS Solutions Builders',
    license='ASL',
    zip_safe=False,
    packages=['mask_lib'],
    package_dir={'mask_lib': '.'},
    include_package_data=False,
    install_requires=[
        'boto3>1.9.150',
        'pillow>=6.0.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
)
