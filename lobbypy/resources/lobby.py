from mongoengine import *
from mongoengine import signals
from player import Player

import logging

log = logging.getLogger(__name__)

class LobbyPlayer(EmbeddedDocument):
    player = ReferenceField(Player, unique=True)
    team = IntField(min_value=0, max_value=2)

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
