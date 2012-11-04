import unittest, transaction
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

def _registerRoutes(config):
    from lobbypy.views import *
    from lobbypy.views.socketio_service import socketio_service
    from lobbypy.lib.auth import group_lookup
    config.add_route('index', '/')
    config.add_view(index, route_name='index',
                renderer='lobbypy:templates/index.pt')
    config.add_route('login', '/login')
    config.add_view(login, route_name='login')
    config.add_route('logout', '/logout')
    config.add_view(logout, route_name='logout')
    # Ajax views
    config.add_route('create_lobby', '/_ajax/lobby/create')
    config.add_view(create_lobby_ajax, route_name='create_lobby', renderer='json')
    config.add_route('all_lobbies', '/_ajax/lobby/all')
    config.add_view(all_lobbies_ajax, route_name='all_lobbies', renderer='json')
    config.add_route('lobby_state', '/_ajax/lobby/{lobby_id}')
    config.add_view(lobby_state_ajax, route_name='lobby_state', renderer='json')
    # Socket.io views
    config.add_route('socket_io', '/socket.io/*remaining')
    config.add_view(socketio_service, route_name='socket_io', renderer='string')

class AjaxCreateTests(unittest.TestCase):
        def setUp(self):
            self.session = _initTestingDB()
            self.config = testing.setUp()

        def tearDown(self):
            self.session.remove()
            testing.tearDown()

        def _callFUT(self, request):
            from lobbypy.views import create_lobby_ajax
            return create_lobby_ajax(request)

        def test_create(self):
            from lobbypy.models import Lobby, Player
            request = testing.DummyRequest()
            request.params['name'] = 'name'
            with transaction.manager:
                player = Player(1)
                self.session.add(player)
            self.config.testing_securitypolicy(userid=
                    1, permissive=True)
            _registerRoutes(self.config)
            info = self._callFUT(request)
            lobby = self.session.query(Lobby).first()
            self.assertEquals(info['lobby_id'], lobby.id)

        def test_duplicate_owners(self):
            from lobbypy.models import Lobby, Player, DBSession
            request = testing.DummyRequest()
            request.params['name'] = 'name'
            with transaction.manager:
                player = Player(1)
                self.session.add(player)
                lobby = Lobby('OG Lobby', player)
                self.session.add(lobby)
            self.config.testing_securitypolicy(userid=
                    1, permissive=True)
            _registerRoutes(self.config)
            info = self._callFUT(request)
            self.assertEquals(info['error'], 'prexisting_lobby')
