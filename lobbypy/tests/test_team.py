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
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        info = instance.__json__(None)
        self.assertEquals(info['name'], 'Red')
        self.assertEquals(len(info['players']), 0)

    def test_is_ready(self):
        from lobbypy.models import Player, LobbyPlayer
        player = Player(0)
        instance = self._makeOne()
        for i in range(9):
            player = Player(i)
            class_num = i % 9 + 1
            lp = LobbyPlayer(player, class_num)
            lp.ready = True
            instance.players.append(lp)
        self.assertTrue(instance.is_ready())

    def test_has_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        self.assertTrue(instance.has_player(player))

    def test_has_class(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player, 1)
        instance.players.append(lp)
        self.assertTrue(instance.has_class(1))

    def test_get_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        self.assertEquals(instance.get_player(player), lp)

    def test_get_player_does_not_exist(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        self.assertRaises(ValueError, instance.get_player, player)

    def test_get_player_dupe_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        instance.players.append(lp)
        self.assertRaises(ValueError, instance.get_player, player)

    def test_append(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.append(lp)
        self.assertEquals(len(instance.players), 1)
        self.assertEquals(instance.players[0], lp)

    def test_append_full(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        for i in range(9):
            instance.players.append(lp)
        self.assertRaises(ValueError, instance.append, lp)

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

    def test_pop_player_does_not_exist(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(1)
        self.assertRaises(ValueError, instance.pop_player, player)

    def test_pop_player_dupe_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        instance.players.append(lp)
        self.assertRaises(ValueError, instance.pop_player, player)

    def test_remove_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        instance.remove_player(player)
        self.assertEquals(len(instance.players), 0)

    def test_remove_player_does_not_exist(self):
        from lobbypy.models import Player
        instance = self._makeOne()
        player = Player(1)
        self.assertRaises(ValueError, instance.remove_player, player)

    def test_remove_player_dupe_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        instance.players.append(lp)
        self.assertRaises(ValueError, instance.remove_player, player)

    def test_remove_player(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        instance.remove_player(player)
        self.assertEquals(len(instance.players), 0)

    def test_set_class(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        instance.set_class(player, 1)
        self.assertEquals(instance.players[0].cls, 1)

    def test_set_class_bad_class(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        player = Player(1)
        lp = LobbyPlayer(player)
        instance.players.append(lp)
        self.assertRaises(ValueError, instance.set_class, player, 0)

    def test_set_class_dupe_class(self):
        from lobbypy.models import Player, LobbyPlayer
        instance = self._makeOne()
        playerA = Player(1)
        lpA = LobbyPlayer(playerA, 1)
        instance.players.append(lpA)
        playerB = Player(2)
        lpB = LobbyPlayer(playerB)
        instance.players.append(lpB)
        self.assertRaises(ValueError, instance.set_class, playerB, 1)
