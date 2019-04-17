from setuptools import find_packages, setup

version = '1.0a13.dev0'
description = open("README.rst").read() + "\n" + open("CHANGES.rst").read()

setup(
    name='collective.redirectacquired',
    version=version,
    description="Redirect when traversing to acquired content outside the current path.",  # noqa
    long_description=description,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords='traversal acquisition',
    author='Godefroid Chapelle',
    author_email='gotcha@bubblenet.be',
    url='https://github.com/collective/collective.redirectacquired',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFCore',
        'Products.CMFPlone',
        'Zope2',  # ZPublisher
        'zExceptions',
        'zope.component',
        'zope.interface',
    ],
    extras_require={
        'test': [
            'Products.CMFPlone[test]'
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
