collective.redirectacquired
===========================

This Plone addon aims to solve the very common issue of having a lot of different URLs that publish the same content item via acquisition.

It supports Plone 6. See 1.x branch for Plone 4 support.

Zope implicit acquisition leads to many use case where URLs that are valid for the publisher are produced but are not the URLs meant by the users of the system.

This addon modifies the publication process to ensure that instead of allowing traversal from a content item to another content item
via  acquisition, we redirect to the URL of the traversed content item.

In the previous paragraph, an item is considered a content item if and only if it provides ``Products.CMFCore.IContentish``.

This should avoid false positive redirects for URL path item that are acquired but are actually parts of the software rather than content items.

If you need to enable publication of content items via acquisition, mark them with
``collective.redirectacquired.interfaces.IPublishableThroughAcquisition``.
