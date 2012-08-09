from collections import (LobbyCollection, MatchCollection, PlayerCollection,
                                ServerCollection)
def _assign(obj, name, parent):
    obj.__name__ = name
    obj.__parent__ = parent
    return obj

class Root(object):
    """
    Root of lobby system ie monogdb
    """
    __name__ = None
    __parent__ = None
    collections = {'lobby':LobbyCollection, 'match':MatchCollection,
            'player':PlayerCollection, 'server':ServerCollection}
    def __init__(self, request):
        self.db = request.db

    def __getitem__(self, name):
        return _assign(self.collections[name](self.db[name]), name, self)

    def __len__(self):
        return len(self.db)

    def __iter__(self):
        return iter(self.db)
