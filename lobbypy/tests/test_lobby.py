from lobbypy.resources.singletons import Lobby
from pyramid import testing

from bson.objectid import ObjectId
import unittest
class LobbyTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def _makeOne(self, **kwargs):
        _id = kwargs['_id'] if '_id' in kwargs else ObjectId()
        name = kwargs['name'] if 'name' in kwargs else _id
        owner_id = kwargs['owner_id'] if 'owner_id' in kwargs else ObjectId()
        players = kwargs['players'] if 'players' in kwargs else [{
            '_id':owner_id, 'team':0}]
        return Lobby(**{'_id':_id, 'name':name,
            'owner_id':owner_id, 'players':players})

    def tearDown(self):
        testing.tearDown()

    def test_join(self):
        """
        Test that a player can join the lobby
        """
        lobby = self._makeOne()
        player_id = ObjectId()
        lobby.join(player_id)
        self.assertTrue(any(map(lambda x: player_id == x['_id'],
            lobby.players)))

    def test_player_rejoin(self):
        """
        Test that an error is raised if a player joins twice
        """
        lobby = self._makeOne()
        player_id = ObjectId()
        lobby.join(player_id)
        self.assertRaises(AssertionError, lobby.join, player_id)

    def test_player_leave(self):
        """
        Test that a player can leave the lobby
        """
        lobby = self._makeOne()
        player_id = ObjectId()
        lobby.players.append({'_id':player_id, 'team':0})
        lobby.leave(player_id)
        self.assertTrue(not any(map(lambda x: player_id == x['_id'],
            lobby.players)))

    def test_owner_leave(self):
        """
        Test that an error is raised if the owner leaves
        """
        player_id = ObjectId()
        lobby = self._makeOne(owner_id=player_id)
        self.assertRaises(AssertionError, lobby.leave, player_id)

    def test_unknown_player_leaves(self):
        """
        Test that an error is raised if a player not in the lobby leaves
        """
        lobby = self._makeOne()
        player_id = ObjectId()
        self.assertRaises(AssertionError, lobby.leave, player_id)
