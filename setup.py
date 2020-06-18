from setuptools import setup

# Get the version from the package. This allows the version to be
# available inside the package for use at runtime.
__version__ = None  # Will get set in next line
# pylint: disable=exec-used
exec(open("sigsci_site_manager/__version__.py").read())

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="sigsci_site_manager",
    version=__version__,
    author="Turner ISO",
    author_email="isodev@turner.com",
    description="Utility for managing Signal Sciences sites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=("https://github.com/turnerlabs/sigsci_site_manager"),
    packages=['sigsci_site_manager'],
    setup_requires=[
        'pytest-runner'
    ],
    install_requires=[
        'pysigsci>=3.10.0'
    ],
    tests_require=[
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'sigsci_site_manager=sigsci_site_manager.site_manager:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Environment :: Console",
        "Topic :: Security"
    ]
)
