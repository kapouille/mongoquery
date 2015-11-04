from setuptools import setup, find_packages
import os

HERE = os.path.dirname(__file__)

def read_file(filename):
    with open(os.path.join(HERE, filename)) as fh:
        return fh.read().strip(' \t\n\r')

README = read_file("README.rst")

setup(
    name='mongoquery',
    version=read_file("VERSION.txt"),
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities"
    ],
    author='Olivier Carrere',
    description="A utility library that provides a MongoDB-like query "
                "language for querying python collections. It's mainly "
                "intended to parse objects structured as fundamental types in "
                "a similar fashion to what is produced by JSON or YAML "
                "parsers.",
    long_description=README,
    author_email='olivier.carrere@gmail.com',
    url='http://github.com/kapouille/mongoquery',
    keywords='mongodb query match',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False
)
