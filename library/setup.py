"""Setup configuration for confmanager-nci library."""

from setuptools import setup, find_packages

setup(
    name="confpapers-nci",
    version="1.0.0",
    author="Srinidhi Vutkoori",
    author_email="srinidhi.vutkoori@example.com",
    description="Academic Conference Paper Submission System Library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
