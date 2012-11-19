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

    def test_len(self):
        instance = self._makeOne()
        self.assertEquals(len(instance), 1)

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

    def test_is_ready(self):
        from lobbypy.models import Player, LobbyPlayer
        player = Player(0)
        instance = self._makeOne(player=player)
        for i in range(18):
            player = Player(i)
            class_num = i % 9 + 1
            lp = LobbyPlayer(player, class_num)
            team_num = 0 if i < 9 else 1
            instance.teams[team_num].append(lp)
        self.assertTrue(instance.is_ready())

    def test_has_player(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.spectators.append(player)
        self.assertTrue(instance.has_player(player))

    def test_on_team(self):
        from lobbypy.models import Player
        playerA = Player(1)
        playerB = Player(2)
        instance = self._makeOne(player=playerA)
        instance.teams[0].append_player(playerB)
        self.assertTrue(instance.on_team(playerB))
        self.assertTrue(not instance.on_team(playerA))

    def test_get_team(self):
        from lobbypy.models import Player
        player = Player(2)
        instance = self._makeOne()
        instance.teams[0].append_player(player)
        self.assertEquals(instance.get_team(player), instance.teams[0])

    def test_get_team_player_off_team(self):
        from lobbypy.models import Player
        player = Player(2)
        instance = self._makeOne(player=player)
        self.assertRaises(ValueError, instance.get_team, player)

    def test_get_team_multiple_teams(self):
        from lobbypy.models import Player
        player = Player(2)
        instance = self._makeOne()
        instance.teams[0].append_player(player)
        instance.teams[1].append_player(player)
        self.assertRaises(ValueError, instance.get_team, player)

    def test_is_ready_player(self):
        from lobbypy.models import Player
        player = Player(2)
        instance = self._makeOne()
        instance.teams[0].append_player(player)
        self.assertTrue(not instance.is_ready_player(player))
        instance.teams[0].players[0].ready = True
        self.assertTrue(instance.is_ready_player(player))

    def test_join(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.join(player)
        self.assertTrue(player in instance.spectators)

    def test_join_dupe_player(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        self.assertRaises(ValueError, instance.join, player)

    def test_leave_spec(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.spectators.append(player)
        instance.leave(player)
        self.assertTrue(player not in instance.spectators)

    def test_leave_team(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.teams[0].append_player(player)
        instance.leave(player)
        self.assertEquals(len(instance.teams[0].players), 0)

    def test_leave_owner(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        self.assertRaises(ValueError, instance.leave, player)

    def test_leave_no_player(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        self.assertRaises(ValueError, instance.leave, player)

    def test_set_team_spec_team(self):
        from lobbypy.models import Player
        player = Player(1)
        instance = self._makeOne(player=player)
        instance.set_team(player, 0)
        self.assertEquals(instance.teams[0].players[0].player, player)

    def test_set_team_team_spec(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.teams[0].append_player(player)
        instance.set_team(player, None)
        self.assertTrue(player in instance.spectators)

    def test_set_team_team_team(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.teams[0].append_player(player)
        instance.set_team(player, 1)
        self.assertEquals(instance.teams[1].players[0].player, player)

    def test_set_class(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.teams[0].append_player(player)
        instance.set_class(player, 1)
        self.assertEquals(instance.teams[0].players[0].cls, 1)

    def test_toggle_ready(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(2)
        instance.teams[0].append_player(player)
        instance.toggle_ready(player)
        self.assertTrue(instance.teams[0].players[0].ready)
