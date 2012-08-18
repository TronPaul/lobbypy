from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from mongo import connect

from lobbypy.resources.root import Root

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    # RED PYRO NEEDS CHANGE BADLY
    my_session_factory = UnencryptedCookieSessionFactoryConfig('bonk')
    config = Configurator(settings=settings, root_factory=Root,
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
    config.add_subscriber(add_mongo_db, NewRequest)
    config.scan('lobbypy')
    return config.make_wsgi_app()
