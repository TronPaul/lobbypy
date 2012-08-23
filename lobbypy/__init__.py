from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from mongoengine import connect

from lobbypy.lib.auth import group_lookup
from lobbypy.resources.root import RootFactory

def main(global_config, **settings):
    """ 
    This function returns a WSGI application.
    """
    # RED PYRO NEEDS CHANGE BADLY
    config = Configurator(settings=settings)
    config.add_static_view('static', 'lobbypy:static')
    # MongoDB
    db_name = settings['mongodb.db_name']
    connect(db_name)
    # Steam API Key
    api_key_file = settings['steam_api.key_file']
    config.registry.settings['steam_api.key'] = open(
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
    # Root Factory
    config.set_root_factory(RootFactory)
    # Add routes
    config.add_route('root', pattern='/')
    config.add_route('login', pattern='/login')
    config.add_route('logout', pattern='/logout')
    config.add_route('lobby_create', pattern='/lobby/create')
    config.add_route('lobby', pattern='/lobby/{lobby_id}/')
    config.add_route('lobby_leave', pattern='/lobby/{lobby_id}/leave')
    config.add_route('lobby_set_team', pattern='/lobby/{lobby_id}/_set_team')
    config.add_route('lobby_set_class', pattern='/lobby/{lobby_id}/_set_class')
    config.add_route('lobby_get_players_delta',
            pattern='/lobby/{lobby_id}/_get_players_delta')
    config.add_route('player', pattern='/player/{player_id}/')
    config.scan('lobbypy')
    return config.make_wsgi_app()
