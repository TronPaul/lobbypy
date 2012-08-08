from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import pymongo

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
    def add_mongo_db(event):
        settings = event.request.registry.settings
        url = settings['mongodb.url']
        db_name = settings['mongodb.db_name']
        db = settings['mongodb_conn'][db_name]
        event.request.db = db
    db_uri = settings['mongodb.url']
    MongoDB = pymongo.Connection
    if 'pyramid_debugtoolbar' in set(settings.values()):
        class MongoDB(pymongo.Connection):
            def __html__(self):
                return 'MongoDB: <b>{}></b>'.format(self)
    conn = MongoDB(db_uri)
    config.registry.settings['mongodb_conn'] = conn
    api_key_file = settings['steam.api_key_file']
    config.registry.settings['steam.api_key'] = open(api_key_file).read()
    config.add_subscriber(add_mongo_db, NewRequest)
    config.scan('lobbypy')
    return config.make_wsgi_app()
