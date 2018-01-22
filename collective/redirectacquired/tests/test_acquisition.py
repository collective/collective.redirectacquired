# from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName
from urllib2 import HTTPError
from zope.interface import alsoProvides
import unittest
from collective.redirectacquired.testing import BASE_INTEGRATION_TESTING

import pkg_resources


class TestBadAcquisition(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def assertRequestHasCanonicalURL(self, request, url):
        self.assertEqual(request['CANONICAL_URL'], 'http://nohost' + url)

    def test_no_acquisition(self):
        "no CANONICAL_URL if no acquired content"
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/a_page')
        self.assertTrue('CANONICAL_URL' not in request)

    def test_acquisition(self):
        "CANONICAL_URL if acquired content"
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/a_folder/a_page')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/a_page')
    
    def test_image(self):
        "CANONICAL_URL if acquired content"
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/a_folder/a_image')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/a_image')

    def test_image(self):
        "CANONICAL_URL if acquired content"
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/a_folder/a_image/view')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/a_image/view')

    def test_image_scale(self):
        "CANONICAL_URL if acquired content"
        self.portal.invokeFactory('Image', 'a_image')
        self.assertTrue('a_image' in self.portal.objectIds())
        
        resource_package = 'collective.redirectacquired.tests'  # Could be any module/package name
        resource_path = '/'.join(('resources', 'sunset.png')) 
        sunset_png = pkg_resources.resource_stream(resource_package, resource_path)
        self.portal['a_image'].setImage(sunset_png)

        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/a_folder/a_image/image_mini')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/a_image/image_mini')

    def test_folder_default_page(self):
        "browsing to acquired page should trigger 301"
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal['news'].invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal['news'].objectIds())
        self.portal['news'].manage_addProperty('default_page', 'a_page', 'string')
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/events/news')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/news')
    
    def test_folder_default_page_with_layout(self):
        "browsing to acquired page should trigger 301"
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal['news'].invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal['news'].objectIds())
        self.portal['news'].manage_addProperty('default_page', 'a_page', 'string')
        self.portal['news']['a_page'].manage_addProperty('layout',
                'document_view', 'string')
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/events/news')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/news')

    def test_folder_edit_alias(self):
        "browsing to acquired page should trigger 301"
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/news/events/edit')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/events/edit')

    def test_folder_layout(self):
        "browsing to acquired page should trigger 301"
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.portal['events'].manage_addProperty('layout', 'folder_listing', 'string')
        request = self.layer['request']
        request.traverse('/plone/news/events')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/events')
