from setuptools import setup, find_packages


def readme():
    with open("README.md", 'r') as f:
        return f.read()


setup(
    name="separationsheet_site",
    description="Website for creating and manipulating separation sheets",
    version="0.0.1",
    long_description=readme(),
    author="Brian Balsamo",
    author_email="balsamo@uchicago.edu",
    packages=find_packages(
        exclude=[
        ]
    ),
    include_package_data=True,
    url='https://github.com/bnbalsamo/separationsheet_site',
    install_requires=[
        'Flask'
    ],
    tests_require=[
        'pytest'
    ],
    test_suite='tests'
)
