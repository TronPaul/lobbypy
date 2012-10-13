import unittest

from pyramid import testing

class LobbyPyAuthTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from mongoengine import connect
        connect('testdb')

    def tearDown(self):
        testing.tearDown()
        from lobbypy.resources.player import Player
        Player.drop_collection()

    def test_auth_new_steamid(self):
        ident_url = 'http://steamcommunity.com/openid/id/0000000000000001'
        from lobbypy.lib.auth import openid
        request = testing.DummyRequest()
        # check player list is empty
        from lobbypy.resources.player import Player
        self.assertEqual(Player.objects.count(), 0)
        player, headers = openid(None, request, {'identity_url':ident_url})
        # check steamoid
        self.assertEqual(player.steamid, 1)
        # check headers
        self.assertEqual(len(headers), 0)
        # check players has one item
        self.assertEqual(Player.objects.count(), 1)

    def test_auth_existing_steamid(self):
        ident_url = 'http://steamcommunity.com/openid/id/0000000000000001'
        from lobbypy.lib.auth import openid
        request = testing.DummyRequest()
        from lobbypy.resources.player import Player
        pre_player = Player(steamid=1)
        pre_player.save()
        # check player list len
        self.assertEqual(Player.objects.count(), 1)
        request = testing.DummyRequest()
        player, headers = openid(None, request, {'identity_url':ident_url})
        self.assertEqual(player.steamid, 1)
        # check player list len
        self.assertEqual(Player.objects.count(), 1)
        # check headers
        self.assertEqual(len(headers), 0)

    def test_group_lookup_existing_player(self):
        from lobbypy.lib.auth import group_lookup
        from lobbypy.resources.player import Player
        player_dict = {'steamid':1}
        player = Player(**player_dict)
        player.save()
        request = testing.DummyRequest()
        self.assertEqual(len(group_lookup(player.id, request)), 0)

    def test_group_lookup_no_player(self):
        from lobbypy.lib.auth import group_lookup
        request = testing.DummyRequest()
        self.assertTrue(group_lookup(None, request) is None)
