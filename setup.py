from setuptools import setup, find_packages

setup(
    name="notion-api",
    version="0.1",
    packages=find_packages(where='app'),
    package_dir={'': 'app'},
    test_suite="tests"
)