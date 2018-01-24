collective.redirectacquired
===========================

This Plone addon aims to solve the very common issue of having a lot of different URLs that publish the same content item via acquisition.

Zope implicit acquisition leads to many use case where URLs that are valid for the publisher are produced but are not the URLs meant by the users of the system.  

While publishing a URL, instead of traversing from a content item to another content item 
via  acquisition, redirect to the URL of the traversed content item.

In the previous paragraph, an item is considered a content item if and only if it provides ``Products.CMFCore.IContentish``.

This should avoid false positive redirects for URL path item that are acquired but are actually parts of the software rather than content items.

If you need to enable publication of content items via acquisition, mark them with
``collective.redirectacquired.interfaces.IPublishableThroughAcquisition``.
