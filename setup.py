#!/usr/bin/env python
"""ssh2net network ssh client library"""
import setuptools


__author__ = "Carl Montanari"

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="ssh2net",
    version="2019.10.27",
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="SSH client for network devices built on ssh2-python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/carlmontanari/ssh2net",
    packages=setuptools.find_packages(),
    install_requires=["ssh2-python>=0.18.0-1"],
    extras_require={
        "textfsm": ["textfsm>=1.1.0", "ntc-templates>=1.1.0"],
        "paramiko": ["paramiko>=2.6.0"],
    },
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
