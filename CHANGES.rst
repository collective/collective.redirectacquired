Changelog
=========


2.0a1 (2024-02-08)
------------------

- Plone 6 support (Plone 4 support dropped)
  [gotcha]

- NotFound when acquiring site only raised when redirect is activated in zope.conf
  [gotcha]


1.0a12 (2018-03-20)
-------------------

- less noisy logging
  [gotcha]

- NotFound when acquiring a site
  [gotcha]


1.0a11 (2018-03-12)
-------------------

- Be defensive against circular redirects caused by broken Link objects or broken plone.folders
  [gotcha]


1.0a10 (2018-02-26)
-------------------

- Get rid of code made useless by refactoring.
  More tests
  [gotcha]


1.0a9 (2018-02-20)
------------------

- Refactor for more complex acquisition
  https://github.com/collective/collective.redirectacquired/issues/3
  [gotcha]

- Do not break redirector
  https://github.com/collective/collective.redirectacquired/issues/2
  [gotcha]

- Do not allow to cache permanent redirection
  https://github.com/collective/collective.redirectacquired/issues/1
  [gotcha]


1.0a8 (2018-01-25)
------------------

- Redirect permanently (301)
  [gotcha]


1.0a7 (2018-01-24)
------------------

- Take care of QUERY_STRING.
  [gotcha]

- Do not redirect if REQUEST_METHOD is not GET.
  [gotcha]

1.0a6 (2018-01-24)
------------------

- Fix and test when logging only.
  [gotcha]


1.0a5 (2018-01-24)
------------------

- Fix rushed code.
  [gotcha]


1.0a4 (2018-01-24)
------------------

- Logging is back.
  [gotcha]


1.0a3 (2018-01-24)
------------------

- More tests and refactoring
  [gotcha]


1.0a2 (2018-01-22)
------------------

- More tests
  [gotcha]

- Much simpler implementation
  [gotcha]


1.0a1 (2018-01-17)
------------------

- Remove useless inclusion of CMFPlone in configure.zcml
  [gotcha]


1.0a0 (2018-01-17)
------------------

- Initial release
  [gotcha]
