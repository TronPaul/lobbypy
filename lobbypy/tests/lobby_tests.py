import unittest
from pyramid import testing

class LobbyTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_limit_player_to_one_lobby(self):
        """
        Test that a player is limited to one lobby
        ie player joins 2 lobbies, is dropped from previous
        """
        pass

    def test_destroy_lobby_on_owner_leave(self):
        """
        Test that lobbies are destroyed when the owner leaves
        """
        pass

    def test_destroy_lobby_on_owner_create_new_lobby(self):
        """
        Test that lobbies are destroyed when the owner creates a new lobby
        """
        pass

    def test_player_dropped_on_owner_kick(self):
        """
        Test that players are removed from the lobby if the owner kicks them
        """
        pass

    def test_player_dropped_from_lobby_on_timeout(self):
        """
        Test that if a player times out (no keepalive) they are dropped

        PENDING: until I figure out how to do keep alive
        """
        pass
