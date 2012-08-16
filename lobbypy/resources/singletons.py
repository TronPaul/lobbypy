from lobbypy.lib.steam_api import get_player_summary

class Lobby(object):
    def __init__(self, **kwargs):
        self._id = kwargs['_id']
        self.name = kwargs['name']
        self.players = kwargs['players']
        self.owner_id = kwargs['owner_id']

    def leave(self, player_id):
        if self.owner_id == player_id:
            raise LobbyOwnerLeaveError
        self.players[:] = [p for p in old_lobby.players
                        if p.get('_id') != player_id]

    def join(self, player_id):
        raise NotImplementedError

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
