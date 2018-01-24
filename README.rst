collective.redirectacquired
===========================

While traversing a URL, if we move from a content item to another content item 
through acquisition, we redirect to the URL of the actual content.

An item is considered a content item if it provides ``Products.CMFCore.IContentish``.

This should avoid false positive redirects for URL path item that are actually part of the software rather than content.

If there are some content items that should be publishable trhough acquisition, mark them with
``collective.redirectacquired.interfaces.IPublishableThroughAcquisition``.
