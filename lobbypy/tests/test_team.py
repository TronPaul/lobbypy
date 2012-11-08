import unittest
from pyramid import testing

class TeamModelTest(unittest.TestCase):
    def _getTargetClass(self):
        from lobbypy.models import Team
        return Team

    def _makeOne(self, name='Red'):
        return self._getTargetClass()(name)

    def test_create(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'Red')
        self.assertEqual(len(instance.players), 0)

    def test_len(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        self.assertEquals(len(instance), 0)
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        self.assertEquals(len(instance), 1)

    def test_json(self):
        pass

    def test_has_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        self.assertTrue(instance.has_player(player))

    def test_get_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        self.assertEquals(instance.get_player(player), lp)

    def test_append(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.append(lp)
        self.assertEquals(len(instance.players), 1)
        self.assertEquals(instance.players[0], lp)

    def test_remove(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        instance.remove(lp)
        self.assertEquals(len(instance.players), 0)

    def test_append_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        instance.append_player(player)
        self.assertEquals(len(instance.players), 1)
        self.assertEquals(instance.players[0].player, player)

    def test_pop_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        self.assertEquals(instance.pop_player(player), lp)
        self.assertEquals(len(instance.players), 0)

    def test_remove_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        instance.remove_player(player)
        self.assertEquals(len(instance.players), 0)

    def test_set_class(self):
        pass
