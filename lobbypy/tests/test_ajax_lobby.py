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

def _registerRoutes(config):
    from lobbypy.views import (
            create_lobby_ajax,
            all_lobbies_ajax,
            lobby_state_ajax,
            )
    from lobbypy.views.socketio_service import socketio_service
    from lobbypy.lib.auth import group_lookup
    # Ajax views
    config.add_route('create_lobby', '/_ajax/lobby/create')
    config.add_view(create_lobby_ajax, route_name='create_lobby', renderer='json')
    config.add_route('all_lobbies', '/_ajax/lobby/all')
    config.add_view(all_lobbies_ajax, route_name='all_lobbies', renderer='json')
    config.add_route('lobby_state', '/_ajax/lobby/{lobby_id}')
    config.add_view(lobby_state_ajax, route_name='lobby_state', renderer='json')

class AjaxCreateTests(unittest.TestCase):
        def setUp(self):
            self.session = _initTestingDB()
            self.config = testing.setUp()

        def tearDown(self):
            self.session.remove()
            testing.tearDown()

        def _callFUT(self, request):
            from lobbypy.views import create_lobby_ajax
            return create_lobby_ajax(request, False)

        def test_create(self):
            from lobbypy.models import Lobby, Player
            _registerRoutes(self.config)
            request = testing.DummyRequest()
            request.params['name'] = 'name'
            request.params['rcon_server'] = ''
            request.params['rcon_pass'] = ''
            self.config.testing_securitypolicy(userid=
                    1, permissive=True)
            info = self._callFUT(request)
            lobby = self.session.query(Lobby).first()
            self.assertEquals(info, lobby.id)

        def test_duplicate_owners(self):
            from lobbypy.models import Lobby, Player
            _registerRoutes(self.config)
            request = testing.DummyRequest()
            request.params['name'] = 'name'
            request.params['rcon_server'] = ''
            request.params['rcon_pass'] = ''
            player = self.session.query(Player).first()
            lobby = Lobby('OG Lobby', player, '', '', '')
            self.session.add(lobby)
            self.config.testing_securitypolicy(userid=
                    1, permissive=True)
            info = self._callFUT(request)
            lobby = self.session.query(Lobby).first()
            self.assertEquals(info, lobby.id)

class AjaxAllLobbiesTests(unittest.TestCase):
        def setUp(self):
            self.session = _initTestingDB()
            self.config = testing.setUp()

        def tearDown(self):
            self.session.remove()
            testing.tearDown()

        def _callFUT(self, request):
            from lobbypy.views import all_lobbies_ajax
            return all_lobbies_ajax(request)

        def test_all_lobbies(self):
            from lobbypy.models import Lobby, Player
            player = self.session.query(Player).first()
            lobby = Lobby('', player, '', '', '')
            self.session.add(lobby)
            request = testing.DummyRequest()
            info = self._callFUT(request)
            self.assertEquals(len(info), 1)
            self.assertEquals(info[0], lobby)

class AjaxLobbyStateTests(unittest.TestCase):
        def setUp(self):
            self.session = _initTestingDB()
            self.config = testing.setUp()

        def tearDown(self):
            self.session.remove()
            testing.tearDown()

        def _callFUT(self, request):
            from lobbypy.views import lobby_state_ajax
            return lobby_state_ajax(request)

        def test_lobby_state(self):
            from lobbypy.models import Lobby, Player
            player = self.session.query(Player).first()
            lobby = Lobby('', player, '', '', '')
            self.session.add(lobby)
            request = testing.DummyRequest()
            request.matchdict['lobby_id'] =1
            info = self._callFUT(request)
            self.assertEquals(info, lobby)
