import unittest
import pkg_resources
from zExceptions import Redirect
from collective.redirectacquired.testing import BASE_INTEGRATION_TESTING


class TestBadAcquisition(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def assertRedirect(self, url, redirect_url=''):
        request = self.layer['request']
        request.set('DO_REDIRECT', True)
        with self.assertRaises(Redirect) as cm:
            request.traverse(url)
        self.assertEquals(cm.exception.message, "http://nohost" + redirect_url)

    def test_no_content_acquired(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/a_page')

    def test_content_acquired(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirect('/plone/a_folder/a_page', '/plone/a_page')

    def test_content_multi_acquired(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.assertRedirect('/plone/events/a_folder/a_page', '/plone/a_folder/a_page')

    def test_content_acquired_and_view(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirect('/plone/a_folder/a_page/search', '/plone/a_page/search')
        self.assertRedirect('/plone/a_folder/a_page/@@search',
                '/plone/a_page/@@search')

    def test_resolveuid(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        uid = self.portal['a_page'].UID()
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/a_page/resolveuid/' + uid)
        self.assertRedirect(
            '/plone/a_folder/a_page/resolveuid/' + uid,
            '/plone/a_page/resolveuid/' + uid
        )

    def test_image(self):
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirect('/plone/a_folder/a_image', '/plone/a_image')

    def test_image_view(self):
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirect('/plone/a_folder/a_image/view', '/plone/a_image/view')

    def test_image_scale(self):
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())

        resource_package = 'collective.redirectacquired.tests'
        resource_path = '/'.join(('resources', 'sunset.png'))
        sunset_png = pkg_resources.resource_stream(resource_package, resource_path)
        self.portal['a_image'].setImage(sunset_png)

        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        self.assertRedirect(
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
        self.assertRedirect(
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
        self.assertRedirect(
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
        self.assertRedirect('/plone/events/news', '/plone/news')

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
        self.assertRedirect('/plone/events/news', '/plone/news')

    def test_folder_edit_alias(self):
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.assertRedirect('/plone/news/events/edit', '/plone/events/edit')

    def test_folder_layout(self):
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.portal['events'].manage_addProperty('layout', 'folder_listing', 'string')
        self.assertRedirect('/plone/news/events', '/plone/events')
