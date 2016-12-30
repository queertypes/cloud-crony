import os
import re
from setuptools import setup, find_packages

pip_requires = os.path.join(os.getcwd(), 'tools', 'requirements.txt')

def file_lines(path):
    reqs = None
    with open(path, 'rt') as f:
        reqs = f.read().split()
    return reqs


def parse_version():
    data = None
    with open('README.rst', 'rt') as f:
        data = f.read()
    return '.'.join(re.search(r':version: (\d+)\.(\d+)\.(\d+)', data).groups())


setup(
    name='cloud-crony',
    version=parse_version(),
    author='Allele Dev',
    author_email='allele.dev@gmail.com',
    description='RESTful Scheduling as a Service: Scheduled Tasks for the Cloud.',
    long_description=open('README.rst').read(),
    url='https://github.com/queertypes/cloud-crony',
    packages=find_packages(),
    zip_safe=False,
    install_requires=file_lines(pip_requires),
    include_package_data=True,
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Environment :: Web Environment',
        'Natural Language :: English',
    ),
    license="Apache 2.0",
    keywords="cloud scheduling tasks cron periodic"
)
