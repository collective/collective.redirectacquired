import unittest
import pkg_resources
from zExceptions import Redirect
from zope.interface import alsoProvides
from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from collective.redirectacquired.testing import BASE_INTEGRATION_TESTING
from collective.redirectacquired.testing import BASE_FUNCTIONAL_TESTING
from collective.redirectacquired.interfaces import IPublishableThroughAcquisition


class TestBadAcquisition(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def assertRedirectWhenTraverse(self, traverse_to, redirect_to):
        request = self.layer['request']
        base_url = request['SERVER_URL']
        request.set('MIGHT_REDIRECT', True)
        with self.assertRaises(Redirect) as cm:
            request.traverse(traverse_to)
        self.assertEquals(cm.exception.message, base_url + redirect_to)

    def test_no_content_acquired(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        request = self.layer['request']
        request.set('MIGHT_REDIRECT', True)
        request.traverse('/plone/a_page')

    def test_not_icontentish__acquired(self):
        from OFS.Image import manage_addFile
        manage_addFile(self.portal, id='a_file')
        self.assertTrue('a_file' in self.portal.objectIds())
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        request = self.layer['request']
        request.set('MIGHT_REDIRECT', True)
        request.traverse('/plone/a_file/a_page')
        request.traverse('/plone/a_page/a_file')

    def test_allow_acquired_content(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        alsoProvides(self.portal['a_page'], IPublishableThroughAcquisition)
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.set('MIGHT_REDIRECT', True)
        request.traverse('/plone/a_folder/a_page')
        self.assertRedirectWhenTraverse(
            '/plone/a_page/a_folder',
            '/plone/a_folder'
        )

    def test_content_acquired(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirectWhenTraverse('/plone/a_folder/a_page', '/plone/a_page')

    def test_content_acquired_log_but_no_redirect(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.set('MIGHT_REDIRECT', False)
        request.traverse('/plone/a_folder/a_page')

    def test_content_multi_acquired(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.assertRedirectWhenTraverse('/plone/events/a_folder/a_page', '/plone/a_folder/a_page')

    def test_content_acquired_and_view(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirectWhenTraverse('/plone/a_folder/a_page/search', '/plone/a_page/search')
        self.assertRedirectWhenTraverse('/plone/a_folder/a_page/@@search',
                '/plone/a_page/@@search')

    def test_resolveuid(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        uid = self.portal['a_page'].UID()
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.set('MIGHT_REDIRECT', True)
        request.traverse('/plone/a_page/resolveuid/' + uid)
        self.assertRedirectWhenTraverse(
            '/plone/a_folder/a_page/resolveuid/' + uid,
            '/plone/a_page/resolveuid/' + uid
        )

    def test_image(self):
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirectWhenTraverse('/plone/a_folder/a_image', '/plone/a_image')

    def test_image_view(self):
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirectWhenTraverse('/plone/a_folder/a_image/view', '/plone/a_image/view')

    def test_image_scale(self):
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())

        resource_package = 'collective.redirectacquired.tests'
        resource_path = '/'.join(('resources', 'sunset.png'))
        sunset_png = pkg_resources.resource_stream(resource_package, resource_path)
        self.portal['a_image'].setImage(sunset_png)

        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            '/plone/a_folder/a_image/image_mini',
            '/plone/a_image/image_mini'
        )

    def test_image_images_view(self):
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())

        resource_package = 'collective.redirectacquired.tests'
        resource_path = '/'.join(('resources', 'sunset.png'))
        sunset_png = pkg_resources.resource_stream(resource_package, resource_path)
        self.portal['a_image'].setImage(sunset_png)

        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirectWhenTraverse(
            '/plone/a_folder/a_image/@@images/image/mini',
            '/plone/a_image/@@images/image/mini'
        )

    def test_image_resolveuid_images_view(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())

        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        folder = self.portal['a_folder']
        folder.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in folder.objectIds())

        resource_package = 'collective.redirectacquired.tests'
        resource_path = '/'.join(('resources', 'sunset.png'))
        sunset_png = pkg_resources.resource_stream(resource_package, resource_path)
        folder['a_image'].setImage(sunset_png)
        uid = folder['a_image'].UID()
        self.assertRedirectWhenTraverse(
            '/plone/a_page/a_folder/resolveuid/%s/@@images/image/mini' % uid,
            '/plone/a_folder/resolveuid/%s/@@images/image/mini' % uid
        )

    def test_folder_default_page(self):
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal['news'].invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal['news'].objectIds())
        self.portal['news'].manage_addProperty('default_page', 'a_page', 'string')
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.assertRedirectWhenTraverse('/plone/events/news', '/plone/news')

    def test_folder_default_page_with_layout(self):
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal['news'].invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal['news'].objectIds())
        self.portal['news'].manage_addProperty('default_page', 'a_page', 'string')
        self.portal['news']['a_page'].manage_addProperty('layout',
                'document_view', 'string')
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.assertRedirectWhenTraverse('/plone/events/news', '/plone/news')

    def test_folder_edit_alias(self):
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.assertRedirectWhenTraverse('/plone/news/events/edit', '/plone/events/edit')

    def test_folder_layout(self):
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.portal['events'].manage_addProperty('layout', 'folder_listing', 'string')
        self.assertRedirectWhenTraverse('/plone/news/events', '/plone/events')


class TestFunctional(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
    
    def test_virtual_hosting(self):
        from Products.SiteAccess.VirtualHostMonster import manage_addVirtualHostMonster
        from Products.SiteAccess.VirtualHostMonster import VirtualHostMonster
	manage_addVirtualHostMonster(self.app)
        self.assertTrue(VirtualHostMonster.id in self.app.objectIds())
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        import transaction
        transaction.commit()
        browser = Browser(self.app)
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        url = self.app.absolute_url() + '/VirtualHostBase/http/www.buystuff.com:80/plone/a_page?MIGHT_REDIRECT=1'
        browser.open(url)
        self.assertEqual(url, browser.url)
        url = self.app.absolute_url() + '/VirtualHostBase/http/www.buystuff.com:80/plone/a_folder/a_page?MIGHT_REDIRECT=1'
        browser.open(url)
        self.assertNotEqual(url, browser.url)
        browser.handleErrors = False
        url = self.app.absolute_url() + '/VirtualHostBase/http/www.buystuff.com:80/plone/VirtualHostRoot/_vh_z/a_page?MIGHT_REDIRECT=1'
        browser.open(url)
        self.assertEqual(url, browser.url)
