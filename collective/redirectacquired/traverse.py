from .interfaces import IPublishableThroughAcquisition
from Acquisition import aq_base
from App.config import getConfiguration
from plone.app.caching.operations.utils import doNotCache
from plone.dexterity.browser.traversal import DexterityPublishTraverse
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import ISiteRoot
from zExceptions import NotFound
from zExceptions import Redirect
from zope.component import adapter
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher.interfaces import IPubAfterTraversal

import logging


logger = logging.getLogger("redirect.acquired")


def check_traversal_to_acquired_content(context, request, name, result):
    if is_suspect_acquisition(context, request, name, result):
        logmsg = "when traversing '{}', ({}) is acquired from ({})".format(
            request.get("ACTUAL_URL"),
            "/".join(result.getPhysicalPath()),
            "/".join(context.getPhysicalPath()),
        )
        referer = request.get("HTTP_REFERER", "none")
        if referer:
            logmsg += ", referred from %s" % referer
        logger.info(logmsg)
        if request["REQUEST_METHOD"] != "GET":
            logger.info(
                "no redirect because METHOD is '%s'", request.get("REQUEST_METHOD")
            )
            return
        if ISiteRoot.providedBy(result):
            request.set("IS_SITE_ACQUIRED", True)
        canonical_url = get_canonical_url(request, result.absolute_url())
        # store CANONICAL_URL in order to be able to redirect later in traversal
        request.set("CANONICAL_URL", canonical_url)


@adapter(IPubAfterTraversal)
def redirect(event):
    request = event.request
    canonical_url = request.get("CANONICAL_URL", None)
    if canonical_url is not None:
        query_string = request["QUERY_STRING"]
        if query_string:
            canonical_url = canonical_url + "?" + query_string

        actual_url = request.get("ACTUAL_URL")
        if query_string:
            actual_url = actual_url + "?" + query_string
        if actual_url == canonical_url:
            logger.warning(
                "wants to redirect from '%s' to CANONICAL_URL '%s', do nothing as it would be circular redirect",
                actual_url,
                canonical_url,
            )
            logger.warning(
                "might be due to a broken plone.folder -- object id is missing from container.objectIds()"
            )
            return
        referer_url = request.get("HTTP_REFERER", "")
        if referer_url == canonical_url:
            logger.warning(
                "wants to redirect to CANONICAL_URL '%s' but HTTP_REFERER is '%s'; do nothing as it would be circular redirect to referer",
                canonical_url,
                referer_url,
            )
            return
        logger.info(
            "redirect from '%s' to CANONICAL_URL '%s'", actual_url, canonical_url
        )
        if might_redirect(request):
            if request.get("IS_SITE_ACQUIRED", False):
                raise NotFound
            dummy = None
            doNotCache(dummy, request, request.response)
            raise MovedPermanently(canonical_url)


def is_suspect_acquisition(context, request, name, result):
    # both objects traversed should be contentish
    if (not ISiteRoot.providedBy(result) and not IContentish.providedBy(result)) or (
        not ISiteRoot.providedBy(context) and not IContentish.providedBy(context)
    ):
        return False
    # allow for explicit acquisition
    elif IPublishableThroughAcquisition.providedBy(result):
        return False
    else:
        result_id = result.getId()
        if (result_id not in context.objectIds()) or (
            aq_base(result) is not aq_base(context[result_id])
        ):
            return True
    return False


class MovedPermanently(Redirect):
    pass


def might_redirect(request):
    return (
        MIGHT_REDIRECT
        or request.get("MIGHT_REDIRECT", False)
        or request.form.get("MIGHT_REDIRECT", False)
    )


def get_canonical_url(request, base_url):
    names = list(request["TraversalRequestNameStack"])
    names.append(base_url)
    names.reverse()
    return "/".join(names)


class CheckAcquiredMixin:
    def publishTraverse(self, request, name):
        result = super().publishTraverse(request, name)
        check_traversal_to_acquired_content(self.context, request, name, result)
        return result


class CheckAcquiredPublishTraverse(CheckAcquiredMixin, DefaultPublishTraverse):
    pass


class DexterityCheckAcquiredPublishTraverse(CheckAcquiredMixin,
                                          DexterityPublishTraverse):
    pass


def getRedirectFromConfiguration():
    config = getConfiguration()
    if not hasattr(config, "product_config"):
        return False
    product_config = config.product_config
    if config is None:
        return False
    configuration = product_config.get("collective.redirectacquired", None)
    if configuration is not None:
        return configuration.get("redirect", "False") == "True"
    else:
        return False


MIGHT_REDIRECT = getRedirectFromConfiguration()
