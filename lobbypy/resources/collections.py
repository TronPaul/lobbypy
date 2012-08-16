from singletons import Lobby, Match, Player, Server
from bson.objectid import ObjectId
from pymongo.errors import InvalidId
from pymongo.collection import Collection as MongoCollection
from pymongo.cursor import Cursor as MongoCursor

class WrappedCollection(MongoCollection):
    """
    Generic Mongodb Collection
    """
    def __init__(self, *args, **kwargs):
        super(WrappedCollection, self).__init__(*args, **kwargs)

    def __getitem__(self, name):
        _id = None
        try:
            _id = ObjectId(name)
        except InvalidId:
            raise KeyError
        item = self.find_one(dict(_id=_id))
        if not item:
            raise KeyError
        return item

    def _make_one(self, adict):
        raise NotImplementedError

    def _assign(self, obj, name):
        obj.__name__ = name
        obj.__parent__ = self
        return obj

    def __len__(self):
        return self.count()

    def __iter__(self):
        raise NotImplementedError

    def find(self, *args, **kwargs):
        original_getitem = MongoCursor.__getitem__
        _make_one = self._make_one
        def __getitem_new__(self, key):
            return _make_one(original_getitem(self, key))
        MongoCursor.__getitem__ = __getitem_new__
        cur = super(WrappedCollection, self).find(*args, **kwargs)
        return cur

    def find_one(self, *args, **kwargs):
        item = super(WrappedCollection, self).find_one(*args, **kwargs)
        return self._make_one(item) if item else None

class LobbyCollection(WrappedCollection):
    """
    Collection of lobbies
    """
    def _make_one(self, adict):
        return self._assign(Lobby(**adict), adict['_id'])

class MatchCollection(WrappedCollection):
    """
    Collection of matches
    """
    def _make_one(self, adict, name):
        return self._assign(Match(**adict), adict['_id'])

class PlayerCollection(WrappedCollection):
    """
    Collection of players
    """
    def _make_one(self, adict, name):
        return self._assign(Player(**adict), adict['_id'])

class ServerCollection(WrappedCollection):
    """
    Collection of players
    """
    def _make_one(self, adict, name):
        return self._assign(Server(**adict), adict['_id'])
