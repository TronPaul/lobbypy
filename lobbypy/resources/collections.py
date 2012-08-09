from lobbypy.lib.steam_api import get_player_summary
from bson.objectid import ObjectId
from pymongo.errors import InvalidId

class Collection(object):
    """
    Generic Mongodb Collection
    """
    def __init__(self, collection):
        self.collection = collection

    def __getitem__(self, name):
        _id = None
        try:
            _id = ObjectId(name)
        except InvalidId:
            raise KeyError
        adict = self.collection.find_one(dict(_id=_id))
        return self._make_one(adict, name)

    def _make_one(self, adict, name):
        raise NotImplementedError

    def _assign(self, obj, name):
        obj.__name__ = name
        obj.__parent__ = self
        return obj

    def __len__(self):
        return self.collection.count()

    def __iter__(self):
        raise NotImplementedError

    def insert(self, *args, **kwargs):
        return self.collection.insert(*args, **kwargs)

    def save(self, *args, **kwargs):
        return self.collection.save(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.collection.update(*args, **kwargs)

    def find(self, *args, **kwargs):
        # TODO: wrap a cursor
        for item in self.collection.find(*args, **kwargs):
            yield self._make_one(item, item['_id'])

    def find_one(self, *args, **kwargs):
        return self.collection.find_one(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.collection.remove(*args, **kwargs)

class LobbyCollection(Collection):
    """
    Collection of lobbies
    """
    def _make_one(self, adict, name):
        return self._assign(Lobby(**adict), name)

class MatchCollection(Collection):
    """
    Collection of matches
    """
    def _make_one(self, adict, name):
        return self._assign(Match(**adict), name)

class PlayerCollection(Collection):
    """
    Collection of players
    """
    def _make_one(self, adict, name):
        return self._assign(Player(**adict), name)

class ServerCollection(Collection):
    """
    Collection of players
    """
    def _make_one(self, adict, name):
        return self._assign(Server(**adict), name)

class Lobby(object):
    def __init__(self, **kwargs):
        self._id = kwargs['_id']
        self.name = kwargs['name']
        self.players = kwargs['players']
        self.owner_id = kwargs['owner_id']

class Match(object):
    pass

class Player(object):
    def __init__(self, **kwargs):
        self._id = kwargs['_id']
        self.steamid = kwargs['steamid']

    def __getattr__(self, name):
        if name == 'name':
            # Player name from steam
            return self._get_persona_name()
        elif name == 'avatar_large':
            return self._get_avatar_url('large')
        elif name == 'avatar_medium':
            return self._get_avatar_url('medium')
        elif name == 'avatar_small':
            return self._get_avatar_url()
        raise AttributeError(name)

    def _get_persona_name(self):
        return self._get_player_summary()['personaname']

    def _get_friends(self):
        return self._get_friend_list()

    def _get_avatar_url(self, size='small'):
        summary = self._get_player_summary()
        if size == 'large':
            return summary['avatarfull']
        elif size == 'medium':
            return summary['avatarmedium']
        else:
            return summary['avatar']

    # TODO: cache this
    def _get_player_summary(self):
        # Do Steam API call to get all data from GetPlayerSummaries for steamid
        return get_player_summary(self.steamid)

    # TODO: cache this
    def _get_friend_list(self):
        # Do Steam API call to get all data from GetFriendList for steamid
        pass

class Server(object):
    pass
