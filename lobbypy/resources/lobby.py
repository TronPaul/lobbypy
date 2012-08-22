from mongoengine import *
from mongoengine import signals
from player import Player

import logging

log = logging.getLogger(__name__)

CLASSES = ((0, 'Random'),
           (1, 'Scout'),
           (2, 'Soldier'),
           (3, 'Pyro'),
           (4, 'Demoman'),
           (5, 'Heavy'),
           (6, 'Engineer'),
           (7, 'Medic'),
           (8, 'Sniper'),
           (9, 'Spy'))

TEAMS = ((0, 'Spectator'),
         (1, 'Blue'),
         (2, 'Red'))

class LobbyPlayer(EmbeddedDocument):
    player = ReferenceField(Player, unique=True, primary_key=True)
    team = IntField(min_value=0, max_value=2, choices=TEAMS, default=0, required=True)
    pclass = IntField(min_value=0, max_value=9, choices=CLASSES, default=0, required=True)

    def __eq__(self, other):
        return (self.player == other.player and
                self.team == other.team and
                self.pclass == other.pclass)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.player < other.player:
            return True
        elif self.player == other.player:
            if self.team < other.team:
                return True
            elif self.team == other.team:
                return self.pclass < other.pclass
        return False

    def __le__(self, other):
         return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other):
        if self.player > other.player:
            return True
        elif self.player == other.player:
            if self.team > other.team:
                return True
            elif self.team == other.team:
                return self.pclass > other.pclass
        return False

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __hash__(self):
        return hash((self.player, self.team, self.pclass))

class Lobby(Document):
    name = StringField(required=True)
    owner = ReferenceField(Player, required=True, unique=True)
    players = ListField(field=EmbeddedDocumentField(LobbyPlayer), required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        players = map(lambda x: x.player, document.players)
        # check each player is unique
        assert len(set(players)) == len(players)
        # check that the owner is a player
        assert document.owner in players

signals.pre_save.connect(Lobby.pre_save, sender=Lobby)

# helper methods
def leave_lobbies(player, exclude=None):
    """
    Remove player from lobbies excluding lobby `excluded`
    """
    q_dict = dict(players__player = player)
    if exclude is not None:
        if isinstance(exclude, Lobby):
            exclude = exclude.id
        elif not isinstance(exclude, ObjectId):
            # TODO: raise error here
            pass
        q_dict['id__ne'] = exclude
    # Check if the player is in any lobbies, remove the player from them
    old_lobbies_q = Lobby.objects(**q_dict)
    map(lambda x: log.info('Player with id %s leaving Lobby with id %s' %
            (player.id, x.id)), old_lobbies_q.all())
    old_lobbies_q.update(pull__players__player = player)

def destroy_owned_lobbies(player, exclude=None):
    """
    Destroy lobbies a player owns excluding `excluded`
    """
    q_dict = dict(owner = player)
    if exclude is not None:
        if isinstance(exclude, Lobby):
            exclude = exclude.id
        elif not isinstance(exclude, ObjectId):
            # TODO: raise error here
            pass
        q_dict['id__ne'] = exclude
    owned_lobbies_q = Lobby.objects(**q_dict)
    map(lambda x: log.info('Owner with id %s leaving Lobby with id %s' %
            (player.id, x.id)), owned_lobbies_q.all())
    owned_lobbies_q.delete(True)
