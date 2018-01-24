import logging
from App.config import getConfiguration
from Acquisition import aq_base
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zExceptions import Redirect

from Products.CMFCore.interfaces import IContentish
from plone.app.imaging.traverse import ImageTraverser

from .interfaces import IPublishableThroughAcquisition

logger = logging.getLogger('redirect.acquired')


def log_if_suspect_acquisition(context, request, name, result):
    if not IContentish.providedBy(result) or not IContentish.providedBy(context):
        return
    if not IPublishableThroughAcquisition.providedBy(result):
        result_id = result.getId()
        if ((result_id not in context.objectIds())
                or (aq_base(result) is not aq_base(context[result_id]))):
            logger.warn(
                "when traversing '%s', '%s' (%s) is acquired from "
                "'%s' (%s), referred from %s",
                request.get('ACTUAL_URL'),
                result.absolute_url(),
                '/'.join(result.getPhysicalPath()),
                context.absolute_url(),
                '/'.join(context.getPhysicalPath()),
                request.get('HTTP_REFERER', "none")
            )
            if might_redirect(request):
                canonical_url = get_canonical_url(request, result.absolute_url())
                actual_url = request.get('ACTUAL_URL')
                logger.info("redirect from '%s' to CANONICAL_URL '%s'", request.get('ACTUAL_URL'), canonical_url)
                raise Redirect(canonical_url)


def might_redirect(request):
    return (
       MIGHT_REDIRECT 
       or request.get('MIGHT_REDIRECT', False)
       or request.form.get('MIGHT_REDIRECT', False)
    )


def get_canonical_url(request, base_url):
    names = request['TraversalRequestNameStack']
    names.append(base_url)
    names.reverse()
    return '/'.join(names)


class LogAcquiredPublishTraverse(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        result = super(LogAcquiredPublishTraverse, self).publishTraverse(request, name)
        log_if_suspect_acquisition(self.context, request, name, result)
        return result


class LogAcquiredImageTraverser(ImageTraverser):

    def publishTraverse(self, request, name):
        result = super(LogAcquiredImageTraverser, self).publishTraverse(request, name)
        log_if_suspect_acquisition(self.context, request, name, result)
        return result


def getRedirectFromConfiguration():
    config = getConfiguration()
    if not hasattr(config, 'product_config'):
        return False
    product_config = config.product_config
    if config is None:
        return False
    configuration = product_config.get('collective.redirectacquired', None)
    if configuration is not None:
        return configuration.get('redirect', 'False') == 'True'
    else:
        return False

MIGHT_REDIRECT = getRedirectFromConfiguration()
