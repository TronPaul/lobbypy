import redis, logging, transaction
from json import loads, dumps

from pyramid.security import authenticated_userid

from socketio.namespace import BaseNamespace

from ..models import DBSession, Player, Lobby
from .. import controllers

log = logging.getLogger(__name__)

class LobbyNamespace(BaseNamespace):
    def initialize(self):
        self.user_id = authenticated_userid(self.request)
        self.lobby_id = None

    def listener(self, lobby_id):
        """
        Redis subscription loop
        """
        r = redis.StrictRedis()
        r = r.pubsub()

        log.info('Player[%s] subscribing to lobby/%s' % (self.user_id,
            lobby_id))
        r.subscribe('lobby/%s' % lobby_id)

        for m in r.listen():
            if m['type'] == 'message':
                data =  loads(m['data'])
                if data['event'] == 'update':
                    """
                    Lobby update event
                    """
                    log.debug('Redis sending[update] with %s' % data['lobby'])
                    self.emit('update', data['lobby'])
                elif data['event'] == 'destroy':
                    """
                    Lobby destroyed event
                    """
                    log.debug('Redis sending[destroy]')
                    self.emit('destroy')
                else:
                    log.error('Redis had unknown message type %s' %
                                data['event'])

    def on_join(self, lobby_id):
        """
        Player joins lobby
        """
        log.debug('Using Session[%s]' % DBSession)
        # If we have a player, do the join
        user_id = self.user_id
        if user_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==user_id).first()
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                # Request join
                controllers.join(DBSession, lobby, player)
                transaction.commit()
                self.lobby_id = lobby_id
        # Cause other sockets to leave / Kill the socket listener
        self.spawn(self.listener, lobby_id)

    def on_leave(self):
        """
        Player leaves lobby
        """
        log.debug('Using Session[%s]' % DBSession)
        # If we have a player, do the leave
        lobby_id = self.lobby_id
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==user_id).first()
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                controllers.leave(DBSession, lobby, player)
                transaction.commit()
        self.kill_local_jobs()
        self.lobby_id = None

    def on_set_team(self, team_id):
        """
        Player sets team
        """
        log.debug('Using Session[%s]' % DBSession)
        # If we have a player, do the set team
        lobby_id = self.lobby_id
        team_id = int(team_id) if team_id is not None else None
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==self.user_id).first()
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                controllers.set_team(DBSession, lobby, player, team_id)
                transaction.commit()

    def on_set_class(self, cls):
        """
        Player sets class
        """
        log.debug('Using Session[%s]' % DBSession)
        # If we have a player, do the set class
        lobby_id = self.lobby_id
        cls = int(cls) if cls is not None else None
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==self.user_id).first()
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                controllers.set_class(DBSession, lobby, player, cls)
                transaction.commit()
