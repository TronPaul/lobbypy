import unittest, transaction

from pyramid import testing

def _initTestingDB():
    from sqlalchemy import create_engine
    from lobbypy.models import (
        DBSession,
        Base,
        Player
        )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        player = Player(1)
        DBSession.add(player)
    return DBSession

class LobbyPyAuthTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_auth_new_steamid(self):
        ident_url = 'http://steamcommunity.com/openid/id/0000000000000002'
        from lobbypy.lib.auth import openid
        from lobbypy.models import Player
        request = testing.DummyRequest()
        # check player list is empty
        self.assertEqual(self.session.query(Player).count(), 1)
        player, headers = openid(None, request, {'identity_url':ident_url})
        # check steamoid
        self.assertEqual(player.steamid, 2)
        # check players has two item
        self.assertEqual(self.session.query(Player).count(), 2)

    def test_auth_existing_steamid(self):
        ident_url = 'http://steamcommunity.com/openid/id/0000000000000001'
        from lobbypy.lib.auth import openid
        from lobbypy.models import Player
        player = Player(1)
        self.session.add(player)
        # check player list len
        request = testing.DummyRequest()
        player, headers = openid(None, request, {'identity_url':ident_url})
        self.assertEqual(player.steamid, 1)
        # check player list len
        self.assertEqual(self.session.query(Player).count(), 1)
        # check headers
        self.assertEqual(len(headers), 0)

    def test_group_lookup_existing_player(self):
        from lobbypy.lib.auth import group_lookup
        from lobbypy.models import Player
        request = testing.DummyRequest()
        self.assertEqual(len(group_lookup(1, request)), 0)

    def test_group_lookup_no_player(self):
        from lobbypy.lib.auth import group_lookup
        request = testing.DummyRequest()
        self.assertTrue(group_lookup(None, request) is None)
