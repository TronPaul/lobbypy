import unittest
from pyramid import testing

class PlayerTest(unittest.TestCase):
    def setUp(self):
        key = open('steam_api_key.secret').read().strip()
        self.config = testing.setUp(settings={'steam.api_key':key})
        from mongoengine import connect
        connect('testdb')

    def tearDown(self):
        testing.tearDown()
        from lobbypy.resources import Player, Lobby
        Lobby.drop_collection()
        Player.drop_collection()

    def _makeLobby(self, player, name='Name', players=None):
        from lobbypy.resources.lobby import Lobby, LobbyPlayer
        if players is None:
            players = [LobbyPlayer(player=player, team=0)]
        else:
            players = map(lambda x: LobbyPlayer(player=x, team=0), players)
        return Lobby(name=name, owner=player, players=players)

    def _makeOne(self, steamid=1):
        from lobbypy.resources.player import Player
        return Player(steamid=steamid)

    def test_player_name(self):
        player = self._makeOne(76561197960435530)
        self.assertEquals(player.name, 'Robin')

    def test_player_destroy_owned_all(self):
        playerOwner = self._makeOne()
        playerOwner.save()
        playerOther = self._makeOne(2)
        playerOther.save()
        lobbyTarget = self._makeLobby(playerOwner)
        lobbyTarget.save()
        lobbyOther = self._makeLobby(playerOther, players=[playerOwner, playerOther])
        lobbyOther.save()
        from lobbypy.resources.lobby import Lobby
        self.assertEquals(Lobby.objects.count(), 2)
        playerOwner.destroy_owned_lobbies()
        self.assertEquals(Lobby.objects.count(), 1)
        self.assertEquals(Lobby.objects.first().owner, playerOther)
        
    def test_player_destroy_owned_exclude(self):
        playerOwner = self._makeOne()
        playerOwner.save()
        playerOther = self._makeOne(2)
        playerOther.save()
        lobbyTarget = self._makeLobby(playerOwner)
        lobbyTarget.save()
        lobbyOther = self._makeLobby(playerOther, players=[playerOwner, playerOther])
        lobbyOther.save()
        from lobbypy.resources.lobby import Lobby
        self.assertEquals(Lobby.objects.count(), 2)
        playerOwner.destroy_owned_lobbies(lobbyTarget)
        self.assertEquals(Lobby.objects.count(), 2)
        self.assertEquals(Lobby.objects.first().owner, playerOwner)

    def test_player_leave_lobbies_all(self):
        playerOwner = self._makeOne()
        playerOwner.save()
        playerOther = self._makeOne(2)
        playerOther.save()
        lobbyA = self._makeLobby(playerOwner, players=[playerOwner, playerOther])
        lobbyA.save()
        lobbyB = self._makeLobby(playerOther, players=[playerOwner, playerOther])
        lobbyB.save()
        from lobbypy.resources.lobby import Lobby
        self.assertEquals(Lobby.objects.count(), 2)
        playerOwner.leave_lobbies()
        self.assertEquals(Lobby.objects.count(), 2)
        self.assertEquals(len(Lobby.objects[0].players), 1)
        self.assertEquals(len(Lobby.objects[1].players), 1)

    def test_player_leave_lobbies_exclude(self):
        playerOwner = self._makeOne()
        playerOwner.save()
        playerOther = self._makeOne(2)
        playerOther.save()
        lobbyA = self._makeLobby(playerOwner, players=[playerOwner, playerOther])
        lobbyA.save()
        lobbyB = self._makeLobby(playerOther, players=[playerOwner, playerOther])
        lobbyB.save()
        from lobbypy.resources.lobby import Lobby
        self.assertEquals(Lobby.objects.count(), 2)
        playerOwner.leave_lobbies(lobbyA)
        self.assertEquals(Lobby.objects.count(), 2)
        self.assertEquals(len(Lobby.objects[0].players), 2)
        self.assertEquals(len(Lobby.objects[1].players), 1)
