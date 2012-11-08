import unittest
from pyramid import testing

class LobbyModelTest(unittest.TestCase):
    def _getTargetClass(self):
        from lobbypy.models import Lobby
        return Lobby

    def _makeOne(self, player=None, name='A Lobby'):
        from lobbypy.models import Player
        if player is None:
            player = Player(1)
        return self._getTargetClass()(name, player)

    def test_create(self):
        instance = self._makeOne()
        self.assertEqual(instance.name, 'A Lobby')
        self.assertTrue(instance.owner is not None)
        self.assertEqual(len(instance.spectators), 1)
        self.assertEqual(len(instance.teams), 2)
        self.assertEqual(len(instance.teams[0].players), 0)
        self.assertEqual(len(instance.teams[1].players), 0)

    def test_json(self):
        instance = self._makeOne()
        d = instance.__json__(None)
        self.assertEquals(d['name'], 'A Lobby')
        self.assertEquals(d['owner'].steamid, 1)
        self.assertEquals(len(d['spectators']), 1)
        self.assertEquals(d['spectators'][0].steamid, 1)
        self.assertEquals(len(d['teams']), 2)
        self.assertEquals(len(d['teams'][0]), 0)
        self.assertEquals(len(d['teams'][1]), 0)

    def test_join(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.join(player)
        self.assertTrue(player in instance.spectators)

    def test_leave(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.spectators.append(player)
        instance.leave(player)
        self.assertTrue(player not in instance.spectators)

    def test_has_player(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.spectators.append(player)
        self.assertTrue(instance.has_player(player))

    def test_len(self):
        instance = self._makeOne()
        self.assertEquals(len(instance), 1)
