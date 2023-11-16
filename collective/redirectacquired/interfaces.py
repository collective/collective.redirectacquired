from zope.interface import Interface


class IPublishableThroughAcquisition(Interface):
    """Marker interface that needs to be provided by content that is
    publishable through acquisition.
    """
