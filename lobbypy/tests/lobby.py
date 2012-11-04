import unittest
from pyramid import testing

def _initTestingDB():
    from sqlalchemy import create_engine
    from lobbypy.models import (
        DBSession,
        Base
        )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession

class LobbyModelTest(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        self.session.remove()

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

    def test_switch_teams(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        instance.set_team(player, instance.teams[0])
        self.assertTrue(instance.teams[0].has_player(player))
        self.assertTrue(not instance.teams[1].has_player(player))

        instance.set_team(player, instance.teams[1])
        self.assertTrue(instance.teams[1].has_player(player))
        self.assertTrue(not instance.teams[0].has_player(player))

        instance.set_team(player, None)
        self.assertTrue(player in instance.spectators)

    def test_switch_classes(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        instance.set_team(player, instance.teams[0])
        instance.set_class(player, 1)
        self.assertEqual(instance.teams[0].get_player(player).cls, 1)

        instance.set_class(player, None)
        self.assertEqual(instance.teams[0].get_player(player).cls, None)

    def test_dupe_players_on_single_lobby_spectate(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        self.assertRaises(ValueError, instance.join, player)

    def test_dupe_players_on_single_lobby_on_team(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        instance.set_team(player, instance.teams[0])
        self.assertRaises(ValueError, instance.join, player)

    def test_dupe_classes(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        instance.set_team(player, instance.teams[0])
        instance.set_class(player, 1)
        player2 = Player(2)
        instance.join(player2)
        instance.set_team(player2, instance.teams[0])
        self.assertRaises(ValueError, instance.set_class, player2, 1)

    def test_bad_classes(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        instance.set_team(player, instance.teams[0])
        self.assertRaises(ValueError, instance.set_class, player, 10)

    def test_missing_player(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        self.assertRaises(ValueError, instance.set_class, player, 1)
        self.assertRaises(ValueError, instance.set_team, player,
                instance.teams[0])
        self.assertRaises(ValueError, instance.leave, player)

    def test_lobby_without_owner_as_player(self):
        from lobbypy.models import Player, Lobby
        player = Player(1)
        instance = self._makeOne(player=player)
        self.assertRaises(ValueError, instance.leave, player)
