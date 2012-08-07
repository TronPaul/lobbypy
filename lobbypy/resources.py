class Root(object):
    """
    Root of lobby system ie monogdb
    """
    def __init__(self, request):
        self.request = request

class LobbyCollection(object):
    """
    Mongodb collection of lobbies
    """
    pass

class MatchCollection(object):
    """
    Mongodb collection of matches
    """
    pass

class PlayerCollection(object):
    """
    Mongodb collection of players
    """
    pass

class ServerCollection(object):
    """
    Mongodb collection of players
    """
    pass
