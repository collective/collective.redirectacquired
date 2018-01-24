collective.redirectacquired
===========================

While publishing a URL, instead of traversing from a content item to another content item 
via  acquisition, redirect to the URL of the traversed content item.

In the previous paragraph, an item is considered a content item if and only if it provides ``Products.CMFCore.IContentish``.

This should avoid false positive redirects for URL path item that are actually part of the software rather than content items.

If you need to enable publication of content items via acquisition, mark them with
``collective.redirectacquired.interfaces.IPublishableThroughAcquisition``.
