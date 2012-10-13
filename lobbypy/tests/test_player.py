import unittest
from pyramid import testing

class PlayerTest(unittest.TestCase):
    def setUp(self):
        key = open('steam_api_key.secret').read().strip()
        self.config = testing.setUp(settings={'steam.api_key':key})

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, steamid):
        from lobbypy.resources.player import Player
        return Player(steamid=steamid)

    def test_player_name(self):
        player = self._makeOne(76561197960435530)
        self.assertEquals(player.name, 'Robin')
