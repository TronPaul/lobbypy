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

class ControllerTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        self.session.remove()

    def test_create_lobby(self):
        from lobbypy.models import Player, Lobby
        player = self.session.query(Player).first()
        from lobbypy.controllers import create_lobby
        create_lobby(self.session, 'Lobby', player, '', False)
        lobby = self.session.query(Lobby).first()
        self.assertEquals(lobby.name, 'Lobby')
        self.assertEquals(lobby.owner, player)

    def test_create_lobby_old_lobbies(self):
        from lobbypy.models import Player, Lobby
        player = self.session.query(Player).first()
        lobby = Lobby('Lobby', player, '', '', '')
        self.session.add(lobby)
        transaction.commit()
        from lobbypy.controllers import create_lobby
        player = self.session.merge(player)
        create_lobby(self.session, 'Lobby', player, '', False)
        self.assertEquals(self.session.query(Lobby).count(), 1)
        lobby = self.session.query(Lobby).first()
        self.assertEquals(lobby.name, 'Lobby')
        self.assertEquals(lobby.owner, player)

    def test_destroy_lobby(self):
        from lobbypy.models import Player, Lobby
        player = self.session.query(Player).first()
        lobby = Lobby('Lobby', player, '', '', '')
        self.session.add(lobby)
        transaction.commit()
        from lobbypy.controllers import destroy_lobby
        lobby = self.session.merge(lobby)
        destroy_lobby(self.session, lobby)
        self.assertEquals(self.session.query(Lobby).count(), 0)

    def test_lock_lobby(self):
        pass

    def test_join(self):
        from lobbypy.models import Player, Lobby
        playerA = self.session.query(Player).first()
        playerB = Player(2)
        self.session.add(playerB)
        lobby = Lobby('Lobby', playerA, '', '', '')
        self.session.add(lobby)
        transaction.commit()
        from lobbypy.controllers import join
        lobby = self.session.merge(lobby)
        playerB = self.session.merge(playerB)
        join(self.session, lobby, playerB)
        transaction.commit()
        lobby = self.session.merge(lobby)
        playerB = self.session.merge(playerB)
        self.assertTrue(playerB in lobby.spectators)

    def test_join_old_lobbies(self):
        from lobbypy.models import Player, Lobby
        playerA = self.session.query(Player).first()
        playerB = Player(2)
        playerC = Player(3)
        self.session.add(playerB)
        self.session.add(playerC)
        lobbyA = Lobby('Lobby', playerA, 'A', '', '')
        lobbyB = Lobby('Lobby', playerB, 'B', '', '')
        lobbyA.spectators.append(playerC)
        self.session.add(lobbyA)
        self.session.add(lobbyB)
        transaction.commit()
        from lobbypy.controllers import join
        lobbyB = self.session.merge(lobbyB)
        playerC = self.session.merge(playerC)
        join(self.session, lobbyB, playerC)
        transaction.commit()
        lobbyA = self.session.merge(lobbyA)
        lobbyB = self.session.merge(lobbyB)
        playerC = self.session.merge(playerC)
        self.assertTrue(playerC in lobbyB.spectators)
        self.assertTrue(playerC not in lobbyA.spectators)

    def test_leave(self):
        from lobbypy.models import Player, Lobby
        playerA = self.session.query(Player).first()
        playerB = Player(2)
        self.session.add(playerB)
        lobby = Lobby('Lobby', playerA, '', '', '')
        lobby.spectators.append(playerB)
        self.session.add(lobby)
        transaction.commit()
        from lobbypy.controllers import leave
        lobby = self.session.merge(lobby)
        playerB = self.session.merge(playerB)
        leave(self.session, lobby, playerB)
        transaction.commit()
        lobby = self.session.merge(lobby)
        playerB = self.session.merge(playerB)
        self.assertTrue(playerB not in lobby.spectators)

    def test_set_team(self):
        from lobbypy.models import Player, Lobby
        player = self.session.query(Player).first()
        lobby = Lobby('Lobby', player, '', '', '')
        self.session.add(lobby)
        transaction.commit()
        from lobbypy.controllers import set_team
        lobby = self.session.merge(lobby)
        player = self.session.merge(player)
        set_team(self.session, lobby, player, 0)
        transaction.commit()
        lobby = self.session.merge(lobby)
        player = self.session.merge(player)
        self.assertEquals(lobby.teams[0].players[0].player, player)

    def test_set_class(self):
        from lobbypy.models import Player, Lobby
        player = self.session.query(Player).first()
        lobby = Lobby('Lobby', player, '', '', '')
        lobby.set_team(player, 0)
        self.session.add(lobby)
        transaction.commit()
        from lobbypy.controllers import set_class
        lobby = self.session.merge(lobby)
        player = self.session.merge(player)
        set_class(self.session, lobby, player, 1)
        transaction.commit()
        lobby = self.session.merge(lobby)
        player = self.session.merge(player)
        self.assertEquals(lobby.teams[0].players[0].cls, 1)

    def test_toggle_ready(self):
        from lobbypy.models import Player, Lobby
        player = self.session.query(Player).first()
        lobby = Lobby('Lobby', player, '', '', '')
        lobby.set_team(player, 0)
        self.session.add(lobby)
        transaction.commit()
        from lobbypy.controllers import toggle_ready
        lobby = self.session.merge(lobby)
        player = self.session.merge(player)
        toggle_ready(self.session, lobby, player)
        transaction.commit()
        lobby = self.session.merge(lobby)
        player = self.session.merge(player)
        self.assertTrue(lobby.teams[0].players[0].ready)
