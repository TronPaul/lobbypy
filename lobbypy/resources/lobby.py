from mongoengine import *
from player import Player

class LobbyPlayer(EmbeddedDocument):
    player = ReferenceField(Player)
    team = IntField(min_value=0, max_value=2)

class Lobby(Document):
    name = StringField(required=True)
    owner = ReferenceField(Player, required=True)
    players = ListField(field=EmbeddedDocumentField(LobbyPlayer), required=True)

