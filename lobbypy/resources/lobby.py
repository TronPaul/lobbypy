from mongoengine import *
from mongoengine import signals

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
    from player import Player
    player = ReferenceField(Player, unique=True, primary_key=True)
    team = IntField(min_value=0, max_value=2, choices=TEAMS, default=0, required=True)
    pclass = IntField(min_value=0, max_value=9, choices=CLASSES, default=0, required=True)

class Lobby(Document):
    from player import Player
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
