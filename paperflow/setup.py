"""
Setup script for the PaperFlow library.
Enables installation via pip install -e . for development.
"""

from setuptools import setup, find_packages

setup(
    name='paperflow',
    version='1.0.0',
    description='Academic Conference Paper Management Library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Srinidhi Vutkoori',
    author_email='x25173243@student.ncirl.ie',
    url='https://github.com/x25173243/paperflow',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[],
    extras_require={
        'dev': ['pytest>=7.0', 'pytest-cov>=4.0']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering',
    ],
    keywords='academic conference paper review submission scoring',
)
