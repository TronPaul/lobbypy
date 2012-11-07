import redis, logging
from json import loads, dumps

from mongoengine import OperationError

from socketio.namespace import BaseNamespace

log = logging.getLogger(__name__)

class LobbiesNamespace(BaseNamespace):
    """
    Namespace for lobby listing
    """
    def initialize(self):
        self.player = self.request.player if hasattr(self.request, 'player') else None

    def listener(self):
        """
        Redis subscription loop
        """
        r = redis.StrictRedis()
        r = r.pubsub()

        r.subscribe('lobbies')

        for m in r.listen():
            if m['type'] == 'message':
                data = loads(m['data'])
                if data['event'] == 'create':
                    """
                    Create lobby event
                    """
                    log.debug('Redis sending[create] with %s' % data['lobby'])
                    self.emit('create', data['lobby'])
                elif data['event'] == 'destroy':
                    """
                    Destroy lobby event
                    """
                    log.debug('Redis sending[destroy] with %s' % data['lobby_id'])
                    self.emit('destroy', data['lobby_id'])
                elif data['event'] == 'update':
                    """
                    Update lobby event
                    """
                    log.debug('Redis sending[update] with %s' % data['lobby'])
                    self.emit('update', data['lobby'])
                else:
                    log.error('Redis had unknown message type %s' %
                            data['event'])

    def on_subscribe(self):
        """
        Client subscribes to Redis
        """
        self.spawn(self.listener)

    def on_unsubscribe(self):
        """
        Client unsubscribes to Redis
        """
        self.kill_local_jobs()
