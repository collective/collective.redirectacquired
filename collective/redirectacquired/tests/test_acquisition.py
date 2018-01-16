# from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName
from urllib2 import HTTPError
from zope.interface import alsoProvides
import unittest
from collective.redirectacquired.testing import BASE_FUNCTIONAL_TESTING


class TestBadAcquisition(unittest.TestCase):

    layer = BASE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.workflowTool = getToolByName(self.portal, 'portal_workflow')
        self.workflowTool.setChainForPortalTypes(('Document', 'Folder'), 'simple_publication_workflow')

    def test_page(self):
        "browsing to acquired page should trigger 301"
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        import transaction
        transaction.commit()
        browser = Browser(self.app)
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        url = self.portal.absolute_url() + '/a_folder/a_page'
        browser.open(url)
        #TODO should be no document_view
        self.assertEqual('http://nohost/plone/a_page/document_view', browser.url)
        url = self.portal.absolute_url() + '/a_folder/a_page/edit'
        browser.open(url)
        self.assertEqual('http://nohost/plone/a_page/edit', browser.url)
    
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
        import transaction
        transaction.commit()
        browser = Browser(self.app)
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        url = self.portal.absolute_url() + '/news/events'
        browser.open(url)
        self.assertEqual('http://nohost/plone/events', browser.url)
        url = self.portal.absolute_url() + '/news/events/edit'
        browser.open(url)
        self.assertEqual('http://nohost/plone/events/edit', browser.url)
