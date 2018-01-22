# from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName
from urllib2 import HTTPError
from zope.interface import alsoProvides
import unittest
from collective.redirectacquired.testing import BASE_INTEGRATION_TESTING


class TestBadAcquisition(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def assertRequestHasCanonicalURL(self, request, url):
        self.assertEqual(request['CANONICAL_URL'], 'http://nohost' + url)

    def test_page(self):
        "browsing to acquired page should trigger 301"
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        request = self.layer['request']
        request.traverse('/plone/a_page')
        self.assertTrue('CANONICAL_URL' not in request)
        request.traverse('/plone/a_folder/a_page')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/a_page/document_view')
        
    
    def test_folder(self):
        "browsing to acquired page should trigger 301"
        self.portal.invokeFactory('Folder', 'news')
        self.assertTrue('news' in self.portal.objectIds())
        self.portal['news'].invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal['news'].objectIds())
        self.portal['news'].manage_addProperty('default_page', 'a_page', 'string')
        self.portal.invokeFactory('Folder', 'events')
        self.assertTrue('events' in self.portal.objectIds())
        self.portal['events'].manage_addProperty('layout', 'folder_listing', 'string')
        request = self.layer['request']
        request.traverse('/plone/news/events')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/events')
        request.traverse('/plone/news/events/edit')
        self.assertTrue('CANONICAL_URL' in request)
        self.assertRequestHasCanonicalURL(request, '/plone/events/edit')
