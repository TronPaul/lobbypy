from pyramid.security import Allow

class RootFactory(object):
    __acl__ = [ (Allow, 'system.Authenticated', 'play') ]

    def __init__(self, request):
        pass
