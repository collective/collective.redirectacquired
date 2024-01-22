try:
    from Products.CMFCore import explicitacquisition
    explicitacquisition.SKIP_PTA = True
except ImportError:
    pass
