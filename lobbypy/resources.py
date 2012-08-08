from util import _assign

class Root(object):
    """
    Root of lobby system ie monogdb
    """
    def __init__(self, request):
        self.db = request.db

    def __getitem__(self, name):
        return _assign(self.db[name])

    def __len__(self):
        return len(self.db)

    def __iter__(self):
        return iter(self.db)

class Collection(object):
    """
    Generic Mongodb Collection
    """
    resources = {'lobby':Lobby, 'match':Match,
                    'player':Player, 'server':Server}
    def __init__(self, collection):
        self.collection = collection

    def __getitem__(self, name):
        raise NotImplementedError

    def __len__(self):
        return self.collection.count()

    def __iter__(self):
        raise NotImplementedError

class LobbyCollection(Collection):
    """
    Collection of lobbies
    """
    pass

class MatchCollection(Collection):
    """
    Collection of matches
    """
    pass

class PlayerCollection(Collection):
    """
    Collection of players
    """
    pass

class ServerCollection(Collection):
    """
    Collection of players
    """
    pass

class Lobby(dict):
    pass

class Match(dict):
    pass

class Player(dict):
    pass

class Server(dict):
    pass
