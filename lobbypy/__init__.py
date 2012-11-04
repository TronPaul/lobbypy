from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config

from .models import (
        DBSession,
        Base,
        Lobby,
        Team,
        LobbyPlayer,
        Player,
        )

from .lib.auth import group_lookup

from .views import index, login, logout
from .views.socketio_service import socketio_service
from .views.ajax_lobby import (create_lobby_ajax,
        all_lobbies_ajax, lobby_state_ajax)

def main(global_config, **settings):
    """
    This function returns a WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    # Steam API Key
    api_key_file = settings['steam_api.key_file']
    config.registry.settings['steam.api_key'] = open(
            api_key_file).read().strip()
    # Beaker Session
    settings['session.key'] = open(settings['session.key_file']).read().strip()
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)
    # Authentication policy
    auth_key = open(settings['authentication_policy.key_file']).read().strip()
    authentication_policy = AuthTktAuthenticationPolicy(auth_key, callback=group_lookup)
    config.set_authentication_policy(authentication_policy)
    # Authorization Policy
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authorization_policy)
    # Add routes
    config.add_static_view('static', 'static', cache_max_age=3600)
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
    config.scan()
    return config.make_wsgi_app()
