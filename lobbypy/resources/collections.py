from lobbypy.lib.steam_api import get_player_summary
from bson.objectid import ObjectId
from util import _assign

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
        player = Player(**self.collection.find_one(dict(_id=ObjectId(name))))
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
