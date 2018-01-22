import logging
from App.config import getConfiguration
from Acquisition import aq_base
from ZPublisher.interfaces import IPubAfterTraversal
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.publisher.interfaces import IPublishTraverse
from zope.component import adapter

from Products.CMFCore.interfaces import IContentish
from plone.app.imaging.traverse import ImageTraverser

from .interfaces import IPublishableThroughAcquisition
from .interfaces import IBaseObject

logger = logging.getLogger('redirect.acquired')
CANONICAL_URL = 'CANONICAL_URL'
CANONICAL_TRAVERSAL_NAMESTACK = 'CANONICAL_TRAVERSAL_NAMESTACK'


def log_if_suspect_acquisition(context, request, name, result):
    # do not log when acquired by VirtualHostMonster
    # because of _vh_
    if context.getId() == 'virtual_hosting':
	return
    logger.debug("%s %s", name, repr(result))
    if IContentish.providedBy(result) and not IPublishableThroughAcquisition.providedBy(result):
        result_id = result.getId()
        if ((result_id not in context.objectIds())
                or (aq_base(result) is not aq_base(context[result_id]))):
            request.set(CANONICAL_URL, result.absolute_url())
            request.set(CANONICAL_TRAVERSAL_NAMESTACK, list(request['TraversalRequestNameStack']))
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


def compute_canonical_url(context, request, name):
    canonical_url = request.get(CANONICAL_URL, None)
    if canonical_url is not None:
        if len(request[CANONICAL_TRAVERSAL_NAMESTACK]) == len(request['TraversalRequestNameStack']) + 1:
            request[CANONICAL_TRAVERSAL_NAMESTACK].pop()
            if isDefaultPage(context, name) or isLayout(context, name):
                return
            name = checkAlias(context, request, name)
            if isFTIDefaultView(context, name):
                return
            if name is not None:
                canonical_url = '/'.join([canonical_url, name])
                request.set(CANONICAL_URL, canonical_url)
        else:
            fix_when_directly_provided(request)


def fix_when_directly_provided(request):
    canonical_url = request.get(CANONICAL_URL, None)
    if canonical_url is not None:
        published_count = len(request[CANONICAL_TRAVERSAL_NAMESTACK]) - len(request['TraversalRequestNameStack'])
        names = request[CANONICAL_TRAVERSAL_NAMESTACK][:published_count]
        names.append(canonical_url)
        names.reverse()
        canonical_url = '/'.join(names)
        request.set(CANONICAL_URL, canonical_url)


def isLayout(context, name):
    return name == context.getProperty('layout', None)


def isFTIDefaultView(context, name):
    FTI = context.getTypeInfo()
    return FTI.getProperty('default_view', None) == name


def isDefaultPage(context, name):
    return name == context.getProperty('default_page', None)


def checkAlias(context, request, name):
    if name != request.get('ACTUAL_URL').split('/')[-1]:
        type_info = context.getTypeInfo()
        aliases = type_info.getMethodAliases()
	for key in aliases:
	    if type_info.queryMethodID(key) == name:
		if key == "(Default)":
                    return None
                else:
                    return key
            elif type_info.queryMethodID(key) == '(selected layout)':
                if key == request.get('ACTUAL_URL').split('/')[-1] and isFTIDefaultView(context, name):
                    return key
    return name

class LogAcquiredPublishTraverse(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        result = super(LogAcquiredPublishTraverse, self).publishTraverse(request, name)
        compute_canonical_url(self.context, request, name)
        log_if_suspect_acquisition(self.context, request, name, result)
        return result


class LogAcquiredImageTraverser(ImageTraverser):

    def publishTraverse(self, request, name):
        result = super(LogAcquiredImageTraverser, self).publishTraverse(request, name)
        compute_canonical_url(self.context, request, name)
        log_if_suspect_acquisition(self.context, request, name, result)
        return result



@adapter(IPubAfterTraversal)
def redirect_acquired_content(event):
    request = event.request
    canonical_url = request.get(CANONICAL_URL, None)
    if canonical_url is not None:
        fix_when_directly_provided(request)
        actual_url = request.get('ACTUAL_URL')
        logger.info("redirect from '%s' to CANONICAL_URL '%s'", request.get('ACTUAL_URL'), canonical_url)
        if DO_REDIRECT:
            request.RESPONSE.redirect(canonical_url)


def getRedirectFromConfiguration():
    config = getConfiguration()
    if not hasattr(config, 'product_config'):
        return
    product_config = config.product_config
    if config is None:
        return
    configuration = product_config.get('collective.redirectacquired', None)
    if configuration is not None:
        return configuration.get('redirect', 'False') == 'True'
    else:
        return False

DO_REDIRECT = getRedirectFromConfiguration()
