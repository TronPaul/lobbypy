import redis, logging, transaction
from json import loads, dumps

from socketio.namespace import BaseNamespace

log = logging.getLogger(__name__)

class LobbyNamespace(BaseNamespace):
    def listener(self, lobby_id):
        """
        Redis subscription loop
        """
        r = redis.StrictRedis()
        r = r.pubsub()

        r.subscribe('lobby.%s' % lobby_id)

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
        if player:
            with transaction.manager:
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                # Check if we're not already part of the lobby
                if not lobby.has_player(player):
                    # Leave all other lobbies
                    # Join the lobby
                    lobby.join(player)
        # Cause other sockets to leave / Kill the socket listener
        self.spawn(self.listener, lobby_id)

    def on_leave(self):
        """
        Player leaves lobby
        """
        # If we have a player, do the leave
        if player:
            with transaction.manager:
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                # Check to make sure we're a part of this lobby
                if lobby.has_player(player):
                    # Leave the lobby
                    lobby.leave(player)
                # We're not in the lobby, wtf?
                else:
                    # TODO: error
                    pass
        # Kill the socket listener

    def on_set_team(self, team_id):
        """
        Player sets team
        """
        # If we have a player, do the set team
        if player:
            with transaction.manager:
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                team = lobby.teams[team_id]
                # Check to make sure we're a part of this lobby
                if lobby.has_player(player):
                    # Set the team
                    lobby.set_team(player, team)
                # We're not in the lobby, wtf?
                else:
                    # TODO: error
                    pass

    def on_set_class(self, cls):
        """
        Player sets class
        """
        # If we have a player, do the set class
        if player:
            with transaction.manager:
                lobby = DBSession.query(Lobby).filter_by(id=lobby_id).first()
                # Check to make sure we're a part of this lobby
                if lobby.has_player(player):
                    # Set the class
                    lobby.set_class(player, cls)
                # We're not in the lobby, wtf?
                else:
                    # TODO: error
                    pass
