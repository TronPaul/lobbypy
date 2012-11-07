import redis, logging, transaction
from json import loads, dumps

from pyramid.security import authenticated_userid

from socketio.namespace import BaseNamespace

from ..models import DBSession, Player, Lobby, Team, LobbyPlayer

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

        r.subscribe('lobby/%s' % lobby_id)

        for m in r.listen():
            if m['type'] == 'message':
                data =  loads(m['data'])
                if data['event'] == 'join':
                    """
                    Player join event
                    """
                    pass
                elif data['event'] == 'leave':
                    """
                    Player leave event
                    """
                    pass
                elif data['event'] == 'destroy':
                    """
                    Lobby destroyed event
                    """
                    pass
                elif data['event'] == 'set_class':
                    """
                    Player set class event
                    """
                    pass
                elif data['event'] == 'set_team':
                    """
                    Player set team event
                    """
                    pass
                else:
                    log.error('Redis had unknown message type %s' %
                                data['event'])

    def on_join(self, lobby_id):
        """
        Player joins lobby
        """
        # If we have a player, do the join
        user_id = self.user_id
        if user_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==user_id).first()
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                # Check if we're not already part of the lobby
                if not lobby.has_player(player):
                    # Leave all other lobbies
                    old_lobbies = DBSession.query(Lobby).filter(
                            Lobby.id == Team.lobby_id,
                            LobbyPlayer.team_id == Team.id,
                            LobbyPlayer.player_id == player.steamid).all()
                    [l.leave(player) if l.owner is not player
                            else DBSession.delete(l)for l in old_lobbies]
                    transactoin.commit()
                    # Join the lobby
                    lobby.join(player)
                    transaction.commit()
                self.lobby_id = lobby_id
        # Cause other sockets to leave / Kill the socket listener
        self.spawn(self.listener, lobby_id)

    def on_leave(self):
        """
        Player leaves lobby
        """
        # If we have a player, do the leave
        lobby_id = self.lobby_id
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==user_id).first()
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                # Check to make sure we're a part of this lobby
                if lobby.has_player(player):
                    # Leave the lobby
                    if lobby.owner is not player:
                        lobby.leave(player)
                    else:
                        DBSession.delete(lobby)
                    transaction.commit()
                # We're not in the lobby, wtf?
                else:
                    # TODO: error
                    pass
        else:
            # TODO: error
            pass
        self.kill_local_jobs()
        self.lobby_id = None

    def on_set_team(self, team_id):
        """
        Player sets team
        """
        # If we have a player, do the set team
        lobby_id = self.lobby_id
        team_id = int(team_id) if team_id is not None else None
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==self.user_id).first()
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                team = lobby.teams[team_id] if team_id is not None else None
                # Check to make sure we're a part of this lobby
                if lobby.has_player(player):
                    # Set the team
                    lobby.set_team(player, team)
                    transaction.commit()
                # We're not in the lobby, wtf?
                else:
                    # TODO: error
                    pass

    def on_set_class(self, cls):
        """
        Player sets class
        """
        # If we have a player, do the set class
        lobby_id = self.lobby_id
        cls = int(cls) if cls is not None else None
        user_id = self.user_id
        if user_id and lobby_id:
            with transaction.manager:
                player = DBSession.query(Player).filter(
                        Player.steamid==self.user_id).first()
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                # Check to make sure we're a part of this lobby
                if lobby.has_player(player):
                    # Set the class
                    lobby.set_class(player, cls)
                    transaction.commit()
                # We're not in the lobby, wtf?
                else:
                    # TODO: error
                    pass
