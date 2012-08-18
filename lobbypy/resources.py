from lobbypy.lib.steam_api import get_player_summary

from mongoengine import *

class LobbyPlayer(EmbeddedDocument):
    player = ReferenceField(Player)
    team = IntField(min_value=1, max_value=2)

class Lobby(Document):
    name = StringField(required=True)
    owner = ReferenceField(Player)
    players = ListField(field=EmbeddedDocumentField, required=True)

class Player(Document):
    steamid = StringField(required=True)

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

class Match(Document):
    pass

class Server(Document):
    pass
