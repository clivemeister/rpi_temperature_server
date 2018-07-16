import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "iot_fridge",
    version = "0.0.9",
    author = "Clive Freeman",
    author_email = "clive.freeman@hpe.com",
    description = ("A simulation of a fridge as an IoT device, payment with blockchain, "
                   "fridge replenishment commissioned on an Uber-like subscription app."
                    "Also features a visualisation of a blockchain that services "
                    "the payments and smart contracts."),
    license = "BSD",
    keywords = "iot blockchain demo fridge raspberry pi",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['CherryPy', 'Mako'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
    ],
)
