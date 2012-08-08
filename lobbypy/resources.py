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
    Mongodb collection of lobbies
    """
    pass

class MatchCollection(Collection):
    """
    Mongodb collection of matches
    """
    pass

class PlayerCollection(Collection):
    """
    Mongodb collection of players
    """
    pass

class ServerCollection(Collection):
    """
    Mongodb collection of players
    """
    pass
