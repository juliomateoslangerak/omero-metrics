from setuptools import setup, find_packages

url = "https://github.com/ome/omero_metrics"
version = "0.1.0.dev0"
setup(
    name="OMERO-metrics",
    version="0.1.0",
    description="A webapp to follow microscope performance over time",
    packages=find_packages(),
    keywords=["omero"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Affero General Public License v3 ",  # noqa
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],  # Get strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    author="Oumou DHMINE",
    author_email="OUMOUDHMINE@gmail.com",
    license="AGPLv3",
    url="%s" % url,
    zip_safe=False,
    download_url="%s/v%s.tar.gz" % (url, version),
    include_package_data=True,
    install_requires=["omero-web>=5.26.0"],
    tests_require=["pytest"],
)
