from zope.interface import Interface
from plone.app.imaging.interfaces import IBaseObject as IImagingBaseObject


class IPublishableThroughAcquisition(Interface):
    """Marker interface that needs to be provided by content that is
    publishable through acquisition.
    """


class IBaseObject(IImagingBaseObject):
    """marker interface to avoid using overrides.zcml"""
