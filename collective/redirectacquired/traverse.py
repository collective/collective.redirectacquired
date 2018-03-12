import logging
from zope.component import adapter
from App.config import getConfiguration
from Acquisition import aq_base
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher.interfaces import IPubAfterTraversal
from zExceptions import Redirect

from Products.CMFCore.interfaces import IContentish
from plone.app.imaging.traverse import ImageTraverser
from plone.app.caching.operations.utils import doNotCache

from .interfaces import IPublishableThroughAcquisition

logger = logging.getLogger('redirect.acquired')


def check_traversal_to_acquired_content(context, request, name, result):
    if is_suspect_acquisition(context, request, name, result):
        logmsg = ("when traversing '%s', '%s' (%s) is acquired from "
                "'%s' (%s), referred from %s")
        logger.info(logmsg,
                request.get('ACTUAL_URL'),
                result.absolute_url(),
                '/'.join(result.getPhysicalPath()),
                context.absolute_url(),
                '/'.join(context.getPhysicalPath()),
                request.get('HTTP_REFERER', "none")
            )
        if request['REQUEST_METHOD'] != 'GET':
            logger.info(
                "no redirect because METHOD is '%s'",
                request.get('REQUEST_METHOD')
            )
            return
        canonical_url = get_canonical_url(request, result.absolute_url())
        # store CANONICAL_URL in order to be able to redirect later in traversal
        request.set('CANONICAL_URL', canonical_url)
   

@adapter(IPubAfterTraversal)
def redirect(event):
    request = event.request
    canonical_url = request.get('CANONICAL_URL', None)
    if canonical_url is not None:
        query_string = request['QUERY_STRING']
        if query_string:
            canonical_url = canonical_url + '?' + query_string
        
        actual_url = request.get('ACTUAL_URL')
        if query_string:
            actual_url = actual_url + '?' + query_string
        if actual_url == canonical_url:
            logger.warning("wants to redirect from '%s' to CANONICAL_URL '%s', do nothing as it would be circular redirect", actual_url, canonical_url)
            logger.warning("might be due to a broken plone.folder -- object id is missing from container.objectIds()")
            return
        referer_url = request.get('HTTP_REFERER', '')
        if referer_url == canonical_url:
            logger.warning("wants to redirect to CANONICAL_URL '%s' but HTTP_REFERER is '%s'; do nothing as it would be circular redirect to referer", canonical_url, referer_url)
            return
        logger.info("redirect from '%s' to CANONICAL_URL '%s'", actual_url, canonical_url)
        if might_redirect(request):
            dummy = None
            doNotCache(dummy, request, request.response)
            raise MovedPermanently(canonical_url)


def is_suspect_acquisition(context, request, name, result):
    # both objects traversed should be contentish
    if not IContentish.providedBy(result) or not IContentish.providedBy(context):
        return False
    # allow for explicit acquisition
    elif IPublishableThroughAcquisition.providedBy(result):
        return False
    else:
        result_id = result.getId()
        if ((result_id not in context.objectIds())
                or (aq_base(result) is not aq_base(context[result_id]))):
            return True
    return False


class MovedPermanently(Redirect):
    pass


def might_redirect(request):
    return (
       MIGHT_REDIRECT 
       or request.get('MIGHT_REDIRECT', False)
       or request.form.get('MIGHT_REDIRECT', False)
    )


def get_canonical_url(request, base_url):
    names = list(request['TraversalRequestNameStack'])
    names.append(base_url)
    names.reverse()
    return '/'.join(names)


class LogAcquiredPublishTraverse(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        result = super(LogAcquiredPublishTraverse, self).publishTraverse(request, name)
        check_traversal_to_acquired_content(self.context, request, name, result)
        return result


class LogAcquiredImageTraverser(ImageTraverser):

    def publishTraverse(self, request, name):
        result = super(LogAcquiredImageTraverser, self).publishTraverse(request, name)
        check_traversal_to_acquired_content(self.context, request, name, result)
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
