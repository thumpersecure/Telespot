#!/usr/bin/env python3
"""
telespot - Setup Script
Installs telespot and its dependencies
"""

from setuptools import setup, find_packages
import os

# Read the README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    requirements = []
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name='telespot',
    version='5.0.0b1',
    author='ThumperSecure',
    author_email='',
    description='Multi-Engine Phone Number OSINT Tool',
    long_description=read_file('README.md') if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/thumpersecure/Telespot',
    license='MIT',

    # Package configuration
    py_modules=['telespot'],
    python_requires='>=3.7',
    install_requires=read_requirements(),

    # Entry points for command-line usage
    entry_points={
        'console_scripts': [
            'telespot=telespot:main',
        ],
    },

    # Package metadata
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Utilities',
    ],

    keywords='phone osint search lookup telephone reverse-lookup',

    # Additional files to include
    package_data={
        '': ['config.txt', 'README.md', 'LICENSE'],
    },
    include_package_data=True,
)

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  telespot v5.0-beta Setup                                        ║
╚══════════════════════════════════════════════════════════════════╝

To install telespot:

  Option 1 - Install with pip (recommended):
    pip install -e .

  Option 2 - Install dependencies only:
    pip install -r requirements.txt

  Option 3 - Run directly:
    python telespot.py

After installation, configure API keys:
    telespot --setup

For help:
    telespot --help

""")
