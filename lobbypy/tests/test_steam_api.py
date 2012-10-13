import unittest, os

from pyramid import testing

class SteamApiTests(unittest.TestCase):
    def setUp(self):
        # TODO: make the file be dynamic off of settings
        key = open('steam_api_key.secret').read().strip()
        self.config = testing.setUp(settings={'steam.api_key':key})

    def tearDown(self):
        testing.tearDown()

    def test_get_player_summary_dict(self):
        from lobbypy.lib.steam_api import get_player_summary
        # Test in which I prove I am narcissistic
        player_summary = get_player_summary('76561197999483354')
        self.assertTrue('personaname' in player_summary)

    def test_get_player_summary_with_bad_steamid(self):
        from lobbypy.lib.steam_api import get_player_summary
        # This is a George test name.  There are many like it, but this one is
        # mine.
        self.assertRaises(LookupError, get_player_summary, ('AAAAAAAAAAAA',))
