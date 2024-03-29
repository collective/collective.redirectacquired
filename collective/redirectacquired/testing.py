from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from Products.CMFPlone.testing import ProductsCMFPloneLayer


class BaseLayer(ProductsCMFPloneLayer):
    def setUpZope(self, app, configurationContext):  # pylint: disable=W0613
        import collective.redirectacquired

        self.loadZCML(package=collective.redirectacquired, name="testing.zcml")


BASE = BaseLayer()


BASE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(BASE,), name="collective.redirectacquired:Integration"
)

BASE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BASE,), name="collective.redirectacquired:Functional"
)
