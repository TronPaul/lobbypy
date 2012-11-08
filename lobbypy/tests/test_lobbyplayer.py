import unittest
from pyramid import testing

class LobbyModelTest(unittest.TestCase):
    def _getTargetClass(self):
        from lobbypy.models import LobbyPlayer
        return LobbyPlayer

    def _makeOne(self, player=None, cls=None):
        from lobbypy.models import Player, LobbyPlayer
        if player is None:
            player = Player(1)
        return self._getTargetClass()(player, cls=cls)

    def test_create(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        self.assertEquals(instance.player, player)
        self.assertEquals(instance.cls, None)

    def test_json(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        info = instance.__json__(None)
        self.assertTrue('player' in info)
        self.assertEquals(info['player'], player)
        self.assertTrue('class' in info)
        self.assertEquals(info['class'], None)
