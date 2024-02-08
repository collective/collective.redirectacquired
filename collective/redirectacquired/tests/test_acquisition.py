from collective.redirectacquired.interfaces import (
        IPublishableThroughAcquisition)
from collective.redirectacquired.testing import BASE_FUNCTIONAL_TESTING
from collective.redirectacquired.testing import BASE_INTEGRATION_TESTING
from collective.redirectacquired.traverse import redirect
from plone.namedfile.file import NamedImage
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from zExceptions import NotFound
from zExceptions import Redirect
from zope.interface import alsoProvides
from ZPublisher.pubevents import PubAfterTraversal

import base64
import unittest
from pathlib import Path


def login_as_test_user(request):
    as_string = TEST_USER_NAME + ":" + TEST_USER_PASSWORD
    as_bytes = as_string.encode()
    request._auth = (b"basic " + base64.b64encode(as_bytes)).decode()


class TestBadAcquisition(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        login_as_test_user(self.layer["request"])

    def assertRedirectWhenTraverse(self, traverse_to, redirect_to, **kw):
        request = self.layer["request"]
        base_url = request["SERVER_URL"]
        request.set("MIGHT_REDIRECT", True)
        for key, value in kw.items():
            request.set(key, value)
        with self.assertRaises(Redirect) as cm:
            request.traverse(traverse_to)
            # simulate ZPublisher.Publish
            redirect(PubAfterTraversal(request))
        self.assertTrue("expires" in request.response.headers)
        self.assertTrue("cache-control" in request.response.headers)
        self.assertTrue(
            request.response.headers["cache-control"].startswith("max-age=0")
        )
        self.assertEqual(
            cm.exception.headers['Location'], base_url + redirect_to)

    def test_content_acquired(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            "/plone/a_folder/a_page", "/plone/a_page")

    def test_no_content_acquired(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", True)
        request.traverse("/plone/a_page")

    def test_content_acquired_with_query_string(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            "/plone/a_folder/a_page",
            "/plone/a_page?query_string=1",
            QUERY_STRING="query_string=1",
        )

    def test_content_acquired_method_POST(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", True)
        request.set("REQUEST_METHOD", "POST")
        request.traverse("/plone/a_folder/a_page")

    def test_not_icontentish__acquired(self):
        from OFS.Image import manage_addFile

        manage_addFile(self.portal, id="a_file")
        self.assertTrue("a_file" in self.portal.objectIds())
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", True)
        request.traverse("/plone/a_file/a_page")
        request.traverse("/plone/a_page/a_file")

    def test_allow_acquired_content(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        alsoProvides(self.portal["a_page"], IPublishableThroughAcquisition)
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", True)
        request.traverse("/plone/a_folder/a_page")
        self.assertRedirectWhenTraverse(
            "/plone/a_page/a_folder", "/plone/a_folder")

    def test_content_acquired_log_but_no_redirect(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", False)
        request.traverse("/plone/a_folder/a_page")

    def test_content_multi_acquired(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "events")
        self.assertTrue("events" in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            "/plone/events/a_folder/a_page", "/plone/a_page"
        )

    def test_content_acquired_and_view(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", True)
        request.traverse("/plone/a_page/my_view")
        self.assertRedirectWhenTraverse(
             "/plone/a_folder/a_page/my_view", "/plone/a_page/my_view"
        )
        self.assertRedirectWhenTraverse(
            "/plone/a_folder/a_page/@@my_view", "/plone/a_page/@@my_view"
        )

    def test_resolveuid(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        uid = self.portal["a_page"].UID()
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", True)
        request.traverse("/plone/a_page/resolveuid/" + uid)
        self.assertRedirectWhenTraverse(
            "/plone/a_folder/a_page/resolveuid/" + uid,
            "/plone/a_page/resolveuid/" + uid,
        )

    def test_image(self):
        self.portal.invokeFactory("Image", "a_image")
        self.assertTrue("a_image" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            "/plone/a_folder/a_image", "/plone/a_image")

    def test_image_view(self):
        self.portal.invokeFactory("Image", "a_image")
        self.assertTrue("a_image" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            "/plone/a_folder/a_image/view", "/plone/a_image/view"
        )

    def test_image_images_view(self):
        self.portal.invokeFactory("Image", "a_image")
        self.assertTrue("a_image" in self.portal.objectIds())

        try:
            from importlib.resources import files
            resource_package = "collective.redirectacquired.tests"
            resource_path = Path("resources", "sunset.png")
            data = files(resource_package).joinpath(resource_path).read_bytes()
        except ImportError:
            from importlib.resources import path
            resource_package = "collective.redirectacquired.tests"
            with path(resource_package, "resources") as resources:
                resource_path = resources / "sunset.png"
                data = resource_path.read_bytes()
        self.portal["a_image"].image = NamedImage(
                data, "image/png", "sunset.png")

        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            "/plone/a_folder/a_image/@@images/image/mini",
            "/plone/a_image/@@images/image/mini",
        )

    def test_image_resolveuid_images_view(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())

        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        folder = self.portal["a_folder"]
        folder.invokeFactory("Image", "a_image")
        self.assertTrue("a_image" in folder.objectIds())

        try:
            from importlib.resources import files
            resource_package = "collective.redirectacquired.tests"
            resource_path = Path("resources", "sunset.png")
            data = files(resource_package).joinpath(resource_path).read_bytes()
        except ImportError:
            from importlib.resources import path
            resource_package = "collective.redirectacquired.tests"
            with path(resource_package, "resources") as resources:
                resource_path = resources / "sunset.png"
                data = resource_path.read_bytes()

        folder["a_image"].image = NamedImage(
                data, "image/png", "sunset.png")

        uid = folder["a_image"].UID()
        self.assertRedirectWhenTraverse(
            "/plone/a_page/a_folder/resolveuid/%s/@@images/image/mini" % uid,
            "/plone/a_folder/resolveuid/%s/@@images/image/mini" % uid,
        )

    def test_folder_default_page(self):
        self.portal.invokeFactory("Folder", "news")
        self.assertTrue("news" in self.portal.objectIds())
        self.portal["news"].invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal["news"].objectIds())
        self.portal["news"].manage_addProperty(
            "default_page", "a_page", "string")
        self.portal.invokeFactory("Folder", "events")
        self.assertTrue("events" in self.portal.objectIds())
        self.assertRedirectWhenTraverse("/plone/events/news", "/plone/news")

    def test_folder_default_page_with_layout(self):
        self.portal.invokeFactory("Folder", "news")
        self.assertTrue("news" in self.portal.objectIds())
        self.portal["news"].invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal["news"].objectIds())
        self.portal["news"].manage_addProperty(
            "default_page", "a_page", "string")
        self.portal["news"]["a_page"].manage_addProperty(
            "layout", "document_view", "string"
        )
        self.portal.invokeFactory("Folder", "events")
        self.assertTrue("events" in self.portal.objectIds())
        self.assertRedirectWhenTraverse("/plone/events/news", "/plone/news")

    def test_folder_edit_alias(self):
        self.portal.invokeFactory("Folder", "news")
        self.assertTrue("news" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "events")
        self.assertTrue("events" in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            "/plone/news/events/edit", "/plone/events/edit")

    def test_folder_layout(self):
        self.portal.invokeFactory("Folder", "news")
        self.assertTrue("news" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "events")
        self.assertTrue("events" in self.portal.objectIds())
        self.portal["events"].manage_addProperty(
            "layout", "folder_listing", "string")
        self.assertRedirectWhenTraverse("/plone/news/events", "/plone/events")

    def test_do_nothing_when_redirect_to_itself(self):
        self.portal.invokeFactory("Folder", "news")
        self.assertTrue("news" in self.portal.objectIds())
        self.portal["news"].invokeFactory("Document", "page")
        self.assertTrue("page" in self.portal["news"].objectIds())
        # simulate breakage of 'news' folder
        self.portal["news"].getOrdering().notifyRemoved("page")
        self.assertTrue("page" not in self.portal["news"].objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", True)
        request.traverse("/plone/news/page")
        redirect(PubAfterTraversal(request))

    def test_do_nothing_when_redirect_to_referrer(self):
        self.portal.invokeFactory("Folder", "news")
        self.assertTrue("news" in self.portal.objectIds())
        self.portal.invokeFactory("Link", "link")
        self.assertTrue("link" in self.portal.objectIds())
        request = self.layer["request"]
        request.set("MIGHT_REDIRECT", True)
        request.set("HTTP_REFERER", "http://nohost/plone/link")
        request.traverse("/plone/news/link")
        redirect(PubAfterTraversal(request))

    def test_not_found_when_acquiring_site(self):
        from Products.CMFPlone.factory import addPloneSite

        app = self.layer["app"]
        addPloneSite(
            app,
            "other_plone",
            title="other plone",
            setup_content=False,
            default_language="en",
        )
        request = self.layer["request"]
        request.traverse("/plone/other_plone")
        redirect(PubAfterTraversal(request))
        # raise only if MIGHT_REDIRECT
        request.set("MIGHT_REDIRECT", True)
        with self.assertRaises(NotFound):
            redirect(PubAfterTraversal(request))


class TestFunctional(unittest.TestCase):

    layer = BASE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.app = self.layer["app"]

    def test_moved_permanently(self):
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        import transaction

        transaction.commit()
        browser = Browser(self.app)
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        url = self.app.absolute_url() + "/plone/a_folder/a_page?MIGHT_REDIRECT=1"
        browser.followRedirects = False
        browser.open(url)
        self.assertTrue(browser.headers.get('Status', '').startswith('301'))

    def test_more_complex_acquisition(self):
        self.portal.invokeFactory("Folder", "dir1")
        self.assertTrue("dir1" in self.portal.objectIds())
        folder = self.portal["dir1"]
        folder.invokeFactory("Folder", "dir2")
        self.assertTrue("dir2" in folder.objectIds())
        subfolder = folder["dir2"]
        subfolder.invokeFactory("Document", "page1")
        self.assertTrue("page1" in subfolder.objectIds())
        self.portal.invokeFactory("Folder", "dir3")
        self.assertTrue("dir3" in self.portal.objectIds())
        import transaction

        transaction.commit()
        browser = Browser(self.app)
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        url = (self.app.absolute_url()
               + "/plone/dir1/dir3/dir2/page1?MIGHT_REDIRECT=1")
        browser.open(url)
        redir_url = (self.app.absolute_url()
                     + "/plone/dir1/dir2/page1?MIGHT_REDIRECT=1")
        self.assertEqual(browser.url, redir_url)

    def test_moved_redirector(self):
        """
        check that collective.redirect does not interfere with redirector
        """
        self.portal.invokeFactory("Folder", "dir1")
        self.assertTrue("dir1" in self.portal.objectIds())
        folder = self.portal["dir1"]
        folder.invokeFactory("Folder", "dir2")
        self.assertTrue("dir2" in folder.objectIds())
        subfolder = folder["dir2"]
        subfolder.invokeFactory("Document", "page1")
        self.assertTrue("page1" in subfolder.objectIds())
        self.portal.invokeFactory("Folder", "dir2")
        self.assertTrue("dir2" in self.portal.objectIds())
        import transaction

        transaction.commit()
        folder.manage_renameObjects(["dir2"], ["dir3"])
        self.assertTrue("dir3" in folder.objectIds())
        import transaction

        transaction.commit()
        browser = Browser(self.app)
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        url = (self.app.absolute_url()
               + "/plone/dir1/dir2/page1?MIGHT_REDIRECT=1")
        browser.open(url)
        redir_url = (self.app.absolute_url()
                     + "/plone/dir1/dir3/page1?MIGHT_REDIRECT=1")
        self.assertEqual(browser.url, redir_url)

    def test_virtual_hosting(self):
        from Products.SiteAccess.VirtualHostMonster import (
            manage_addVirtualHostMonster)
        from Products.SiteAccess.VirtualHostMonster import VirtualHostMonster

        manage_addVirtualHostMonster(self.app)
        self.assertTrue(VirtualHostMonster.id in self.app.objectIds())
        self.portal.invokeFactory("Document", "a_page")
        self.assertTrue("a_page" in self.portal.objectIds())
        self.portal.invokeFactory("Folder", "a_folder")
        self.assertTrue("a_folder" in self.portal.objectIds())
        import transaction

        transaction.commit()
        browser = Browser(self.app)
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        url = (
            self.app.absolute_url()
            + "/VirtualHostBase/http/www.buystuff.com:80"
            + "/plone/a_page?MIGHT_REDIRECT=1"
        )
        browser.open(url)
        self.assertEqual(url, browser.url)

        browser.followRedirects = False
        url = (
            self.app.absolute_url()
            + "/VirtualHostBase/http/www.buystuff.com:80"
            + "/plone/a_folder/a_page?MIGHT_REDIRECT=1"
        )
        browser.open(url)
        self.assertTrue(browser.headers.get('Status', '').startswith('301'))

        browser.followRedirects = True
        browser.handleErrors = False
        url = (
            self.app.absolute_url()
            + "/VirtualHostBase/http/www.buystuff.com:80"
            + "/plone/VirtualHostRoot/_vh_z/a_page?MIGHT_REDIRECT=1"
        )
        browser.open(url)
        self.assertEqual(url, browser.url)
