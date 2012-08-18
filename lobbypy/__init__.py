from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from mongoengine import connect

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    # RED PYRO NEEDS CHANGE BADLY
    my_session_factory = UnencryptedCookieSessionFactoryConfig('bonk')
    config = Configurator(settings=settings,
            session_factory = my_session_factory)
    config.add_static_view('static', 'lobbypy:static')
    # MongoDB
    db_name = settings['mongodb.db_name']
    connect(db_name)
    if 'pyramid_debugtoolbar' in set(settings.values()):
        class MongoDB(pymongo.Connection):
            def __html__(self):
                return 'MongoDB: <b>{}></b>'.format(self)
    # Steam API Key
    api_key_file = settings['steam.api_key_file']
    config.registry.settings['steam.api_key'] = open(api_key_file).read().strip()
    # Add routes
    config.add_route('root', pattern='/')
    config.add_route('login', pattern='/login')
    config.add_route('logout', pattern='/logout')
    config.add_route('lobby_create', pattern='/lobby/create')
    config.add_route('lobby', pattern='/lobby/{lobby_id}/')
    config.add_route('lobby_set_team', pattern='/lobby/{lobby_id}/_set_team')
    config.add_route('lobby_set_class', pattern='/lobby/{lobby_id}/_set_class')
    config.add_route('player', pattern='/player/{player_id}/')
    config.scan('lobbypy')
    return config.make_wsgi_app()
