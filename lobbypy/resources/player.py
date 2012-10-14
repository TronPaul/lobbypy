from lobbypy.lib.steam_api import get_player_summary

from mongoengine import *
import logging

log = logging.getLogger(__name__)

class Player(Document):
    steamid = IntField(required=True, unique=True)

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

    def leave_lobbies(self, exclude=None):
        """
        Remove player from lobbies excluding lobby `excluded`
        """
        from lobby import Lobby
        q_dict = dict(players__player = self)
        if exclude is not None:
            if isinstance(exclude, Lobby):
                exclude = exclude.id
            #TODO allow lists of excluded lobbies
            elif not isinstance(exclude, ObjectId):
                # TODO: raise error here
                pass
            q_dict['id__ne'] = exclude
        # Check if the player is in any lobbies, remove the player from them
        old_lobbies_q = Lobby.objects(**q_dict)
        map(lambda x: log.info('Player with id %s leaving Lobby with id %s' %
                (self.id, x.id)), old_lobbies_q.all())
        old_lobbies_q.update(pull__players__player = self)

    def destroy_owned_lobbies(self, exclude=None):
        """
        Destroy lobbies a player owns excluding `excluded`
        """
        from lobby import Lobby
        q_dict = dict(owner = self)
        if exclude is not None:
            if isinstance(exclude, Lobby):
                exclude = exclude.id
            #TODO allow lists of excluded lobbies
            elif not isinstance(exclude, ObjectId):
                # TODO: raise error here
                pass
            q_dict['id__ne'] = exclude
        owned_lobbies_q = Lobby.objects(**q_dict)
        map(lambda x: log.info('Owner with id %s leaving Lobby with id %s' %
                (self.id, x.id)), owned_lobbies_q.all())
        owned_lobbies_q.delete(True)
