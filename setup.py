#!/usr/bin/env python
"""ssh2net network ssh client library"""
import setuptools


__author__ = "Carl Montanari"

with open("README.md", "r") as f:
    readme = f.read()

setuptools.setup(
    name="ssh2net",
    version="2019.09.02",
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="SSH client for network devices built on ssh2-python",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/carlmontanari/ssh2net",
    packages=setuptools.find_packages(),
    install_requires=["ssh2-python>=0.18.0-1"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
)
