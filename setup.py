from setuptools import find_packages
from setuptools import setup


version = "2.0a1"
description = open("README.rst").read() + "\n" + open("CHANGES.rst").read()

setup(
    name="collective.redirectacquired",
    version=version,
    description="Redirect when traversing to acquired content outside the current path.",  # noqa
    long_description=description,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    keywords="traversal acquisition",
    author="Godefroid Chapelle",
    author_email="gotcha@bubblenet.be",
    url="https://github.com/collective/collective.redirectacquired",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Products.CMFCore",
        "Products.CMFPlone",
        "Zope2",  # ZPublisher
        "zExceptions",
        "zope.component",
        "zope.interface",
        "plone.app.caching",
    ],
    python_requires='>=3.7',
    extras_require={"test": ["Products.CMFPlone[test]"]},
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
