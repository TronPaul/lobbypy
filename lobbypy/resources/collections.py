from lobbypy.util import _assign

class Collection(object):
    """
    Generic Mongodb Collection
    """
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
    def __getitem__(self, name):
        lobby = Lobby(self.collection.find_one(dict(_id=ObjectId(name))))
        return _assign(lobby, name, self)

class MatchCollection(Collection):
    """
    Collection of matches
    """
    def __getitem__(self, name):
        match = Match(self.collection.find_one(dict(_id=ObjectId(name))))
        return _assign(match, name, self)

class PlayerCollection(Collection):
    """
    Collection of players
    """
    def __getitem__(self, name):
        player = Player(self.collection.find_one(dict(_id=ObjectId(name))))
        return _assign(player, name, self)

class ServerCollection(Collection):
    """
    Collection of players
    """
    def __getitem__(self, name):
        server = Server(self.collection.find_one(dict(_id=ObjectId(name))))
        return _assign(server, name, self)

class Lobby(object):
    pass

class Match(object):
    pass

class Player(object):
    def __init__(self, **kwargs):
        self.steamid = steamid

class Server(object):
    pass
