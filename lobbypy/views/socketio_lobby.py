import redis, logging, transaction, gevent
from sqlalchemy.orm import joinedload
from json import loads, dumps

from pyramid.security import authenticated_userid

from socketio.namespace import BaseNamespace

from ..models import (
        DBSession,
        Player,
        Lobby,
        prep_json_encode,
        PyramidJSONEncoder,
        )
from .. import controllers

log = logging.getLogger(__name__)

def make_me_state(player_id, lobby_dict):
    if player_id is None:
        me_lp = {
                'player':player_id,
                'on_team':None,
                'ready':None,
                'is_leader':None,
                }
    else:
        me_lp = {
                'player':player_id,
                'on_team':False,
                'ready':None,
                'is_leader':False,
                }
    if lobby_dict['owner']['steamid'] == player_id:
        me_lp['is_leader'] = True
    for team in lobby_dict['teams']:
        lps = [lp for lp in team['players'] if lp['player']['steamid'] == player_id]
        if len(lps) > 0:
            lp = lps.pop()
            me_lp['on_team'] = True
            me_lp['ready'] = lp['ready']
            return me_lp
    return me_lp

class LobbyNamespace(BaseNamespace):
    lobby_id = None
    user_id = None
    def initialize(self):
        self.user_id = authenticated_userid(self.request)

    def get_initial_acl(self):
        return [
                'recv_connect',
                'recv_disconnect',
                'on_join',
               ]

    def listener(self, lobby_id):
        """
        Redis subscription loop
        """
        r = redis.StrictRedis()
        r = r.pubsub()
        user_id = self.user_id

        def i_am_in_lobby(lobby_data):
            """
            Check if the user_id is in the lobby
            """
            players = []
            players.extend(lobby_data['spectators'])
            for team in lobby_data['teams']:
                players.extend([lp['player'] for lp in team['players']])
            return user_id in [p['steamid'] for p in players]

        log.info('Player[%s] subscribing to lobby/%s' % (user_id,
            lobby_id))
        r.subscribe('lobby/%s' % lobby_id)

        for m in r.listen():
            if m['type'] == 'message':
                data =  loads(m['data'])
                if data['event'] == 'update':
                    """
                    Lobby update event
                    """
                    lobby_data = data['lobby']
                    if user_id is None or i_am_in_lobby(lobby_data):
                        log.debug('Redis loop sending[update] with %s' % data['lobby'])
                        self.emit('update', make_me_state(user_id, data['lobby']), data['lobby'])
                    else:
                        log.debug('Redis loop sending[leave]')
                        self.emit('leave')
                elif data['event'] == 'destroy':
                    """
                    Lobby destroyed event
                    """
                    log.debug('Redis sending[destroy]')
                    self.emit('destroy')
                    self.lobby_id = None
                elif data['event'] == 'start':
                    """
                    Lobby start event
                    """
                    log.debug('Redis sending[start]')
                else:
                    log.error('Redis had unknown message type %s' %
                                data['event'])

    def disconnect(self, *args, **kwargs):
        """
        Player disconnects from socketio service
        May need to leave lobby
        """
        log.info('Player[%s] disconnecting from socket' % self.user_id)
        user_id = self.user_id
        lobby_id = self.lobby_id
        if user_id is not None and lobby_id is not None:
                lobby = DBSession.query(Lobby).\
                        options(joinedload('owner'),
                                 joinedload('spectators'),
                                 joinedload('teams'),
                                 joinedload('teams.players'),
                                 joinedload('teams.players.player')).\
                        filter_by(id=lobby_id).first()
                player = DBSession.query(Player).filter(
                        Player.steamid==user_id).first()
                controllers.leave(DBSession, lobby, player)
                transaction.commit()
        super(LobbyNamespace, self).disconnect(*args, **kwargs)

    def on_join(self, lobby_id):
        """
        Player joins lobby
        """
        log.info('Player[%s] emitted join(%s)' % (self.user_id, lobby_id))
        # If we have a player, do the join
        user_id = self.user_id
        with transaction.manager:
            lobby = DBSession.query(Lobby).\
                    options(joinedload('owner'),
                            joinedload('spectators'),
                            joinedload('teams'),
                            joinedload('teams.players'),
                            joinedload('teams.players.player')).\
                    filter_by(id=lobby_id).first()
            if lobby is None:
                # TODO: redirect client to index, give error
                return
            self.lobby_id = lobby_id
            if user_id:
                player = DBSession.query(Player).filter(
                        Player.steamid==user_id).first()
                # Request join
                if not lobby.has_player(player):
                    controllers.join(DBSession, lobby, player)
                    transaction.commit()
            self.add_acl_method('on_set_team')
            self.add_acl_method('on_leave')
            lobby = DBSession.merge(lobby)
            lobby_dict = prep_json_encode(lobby)
            self.emit('update', make_me_state(user_id, lobby_dict), lobby_dict)
            self.spawn(self.listener, lobby_id)

    def on_leave(self):
        """
        Player leaves lobby
        """
        log.info('Player[%s] emitted leave()' % self.user_id)
        # If we have a player, do the leave
        lobby_id = self.lobby_id
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==user_id).first()
                lobby = DBSession.query(Lobby).\
                        options(joinedload('owner'),
                                 joinedload('spectators'),
                                 joinedload('teams'),
                                 joinedload('teams.players'),
                                 joinedload('teams.players.player')).\
                        filter_by(id=lobby_id).first()
                controllers.leave(DBSession, lobby, player)
                transaction.commit()
        self.kill_local_jobs()
        self.lobby_id = None
        self.reset_acl()

    def on_set_team(self, team_id):
        """
        Player sets team
        """
        log.info('Player[%s] emitted set_team(%s)' % (self.user_id, team_id))
        # If we have a player, do the set team
        lobby_id = self.lobby_id
        team_id = int(team_id) if team_id is not None else None
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==self.user_id).first()
                lobby = DBSession.query(Lobby).\
                        options(joinedload('owner'),
                                 joinedload('spectators'),
                                 joinedload('teams'),
                                 joinedload('teams.players'),
                                 joinedload('teams.players.player')).\
                        filter_by(id=lobby_id).first()
                controllers.set_team(DBSession, lobby, player, team_id)
                transaction.commit()
                if team_id is None:
                    self.del_acl_method('on_set_class')
                    self.del_acl_method('on_toggle_ready')
                else:
                    self.add_acl_method('on_set_class')
                    self.add_acl_method('on_toggle_ready')

    def on_set_class(self, cls):
        """
        Player sets class
        """
        log.info('Player[%s] emitted set_class(%s)' % (self.user_id, cls))
        # If we have a player, do the set class
        lobby_id = self.lobby_id
        cls = int(cls) if cls is not None else None
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==self.user_id).first()
                lobby = DBSession.query(Lobby).\
                        options(joinedload('teams'),
                                 joinedload('teams.players'),
                                 joinedload('teams.players.player')).\
                        filter_by(id=lobby_id).first()
                controllers.set_class(DBSession, lobby, player, cls)
                transaction.commit()

    def on_toggle_ready(self):
        """
        Player toggles ready state
        """
        log.info('Player[%s] emitted toggle_ready' % self.user_id)
        lobby_id = self.lobby_id
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==self.user_id).first()
                lobby = DBSession.query(Lobby).\
                        options(joinedload('teams'),
                                 joinedload('teams.players'),
                                 joinedload('teams.players.player')).\
                        filter_by(id=lobby_id).first()
                controllers.toggle_ready(DBSession, lobby, player)
                transaction.commit()
            lobby = DBSession.merge(lobby)
            player = DBSession.merge(player)
            if lobby.is_ready_player(player):
                self.del_acl_method('on_set_team')
                self.del_acl_method('on_set_class')
                if lobby.owner == player:
                    self.add_acl_method('on_start')
            else:
                self.add_acl_method('on_set_team')
                self.add_acl_method('on_set_class')
                if 'on_start' in self.allowed_methods:
                    self.del_acl_method('on_start')

    def on_start(self):
        """
        Lobby owner initiates lobby start
        """
        log.info('Player[%s] emmited start' % self.user_id)
        lobby_id = self.lobby_id
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                lobby = DBSession.query(Lobby).\
                        options(joinedload('teams')).\
                        filter_by(id=lobby_id).first()
                r = redis.Redis()
                r.publish('lobby/%s' % lobby_id, dumps(dict(event='update',
                    lobby=lobby), cls=PyramidJSONEncoder))
                controllers.start_lobby(DBSession, lobby)
                transaction.commit()
