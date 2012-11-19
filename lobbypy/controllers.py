from sqlalchemy import event, or_, and_
from sqlalchemy.orm import joinedload
import transaction

from .models import (
        Lobby,
        Team,
        LobbyPlayer,
        PyramidJSONEncoder,
        DBSession,
        spectator_table,
        )

import logging

log = logging.getLogger(__name__)

def redis_update_lobby(success, lobby):
    import redis
    from json import dumps
    if success:
        r = redis.Redis()
        lobby = DBSession.merge(lobby)
        r.publish('lobbies', dumps(dict(event='update', lobby=lobby),
                cls=PyramidJSONEncoder))
        log.info('Publishing redis[update] to lobby/%s' % lobby.id)
        r.publish('lobby/%s' % lobby.id, dumps(dict(event='update', lobby=lobby),
                cls=PyramidJSONEncoder))

def redis_create_lobby(success, lobby):
    import redis
    from json import dumps
    if success:
        r = redis.Redis()
        lobby = DBSession.merge(lobby)
        r.publish('lobbies', dumps(dict(event='create', lobby=lobby),
                cls=PyramidJSONEncoder))

def redis_destroy_lobby(success, lobby_id):
    import redis
    from json import dumps
    if success:
        r = redis.Redis()
        r.publish('lobbies', dumps(dict(event='destroy', lobby_id=lobby_id)))
        log.info('Publishing redis[destroy] to lobby/%s' % lobby_id)
        r.publish('lobby/%s' % lobby_id, dumps(dict(event='destroy')))

def leave_old_lobbies(session, player):
    """
    Leave all existing lobbies
    """
    spec_lobbies = session.query(Lobby).\
            options(joinedload('spectators')).\
            filter(and_(Lobby.id == spectator_table.c.lobby_id,
            spectator_table.c.player_id == player.steamid
            )).all()
    player_lobbies = session.query(Lobby).\
            options(joinedload('teams'),
                    joinedload('teams.players'),
                    joinedload('teams.players.player')).\
            filter(and_(
            Lobby.id == Team.lobby_id,
            LobbyPlayer.team_id == Team.id,
            LobbyPlayer.player_id == player.steamid
            )).all()
    [leave(session, l, player) for l in spec_lobbies]
    [leave(session, l, player) for l in player_lobbies]

def create_lobby(session, name, player):
    """
    Create a lobby in the database
    """
    log.info('Player[%s] creating lobby' % player.steamid)
    leave_old_lobbies(session, player)
    # create lobby
    lobby = Lobby(name, player)
    session.add(lobby)
    current = transaction.get()
    current.addAfterCommitHook(redis_create_lobby, args=(lobby,))
    return lobby

def destroy_lobby(session, lobby):
    """
    Delete a lobby from the database
    """
    lobby_id = lobby.id
    log.info('Destroying Lobby[%s]' % lobby_id)
    session.delete(lobby)
    current = transaction.get()
    current.addAfterCommitHook(redis_destroy_lobby, args=(lobby_id,))

def lock_lobby(session, lobby):
    """
    Lock lobby, preventing changes
    """
    if lobby.is_ready():
        lobby.lock = True
        current = transaction.get()
        current.addAfterCommitHook(redis_update_lobby, args=(lobby,))

def join(session, lobby, player):
    """
    Add a player to lobby
    """
    if lobby.has_player(player):
        return
    # leave old lobbies
    leave_old_lobbies(session, player)
    # join lobby
    log.info('Player[%s] joinling Lobby[%s]' % (player.steamid, lobby.id))
    lobby.join(player)
    current = transaction.get()
    current.addAfterCommitHook(redis_update_lobby, args=(lobby,))

def leave(session, lobby, player):
    """
    Remove a player from lobby
    """
    log.info('Player[%s] leaving Lobby[%s]' % (player.steamid, lobby.id))
    if lobby.owner is player:
        destroy_lobby(session, lobby)
    else:
        lobby.leave(player)
        current = transaction.get()
        current.addAfterCommitHook(redis_update_lobby, args=(lobby,))

def set_team(session, lobby, player, team_id):
    """
    Set a player's team in lobby
    """
    current = transaction.get()
    log.info('Player[%s] setting team to %s in Lobby[%s]' % (player.steamid,
        team_id, lobby.id))
    lobby.set_team(player, team_id)
    current = transaction.get()
    current.addAfterCommitHook(redis_update_lobby, args=(lobby,))

def set_class(session, lobby, player, cls):
    """
    Set a player's class in lobby
    """
    log.info('Player[%s] setting class to %s in Lobby[%s]' % (player.steamid,
        cls, lobby.id))
    if lobby.on_team(player) and not lobby.get_team(player).has_class(cls):
        lobby.set_class(player, cls)
        transaction.get().addAfterCommitHook(redis_update_lobby, args=(lobby,))

def toggle_ready(session, lobby, player):
    """
    Toggle a ready for a player in lobby
    """
    log.info('Player[%s] toggling ready in Lobby[%s]' % (player.steamid,
        lobby.id))
    if lobby.on_team(player):
        lobby.toggle_ready(player)
        transaction.get().addAfterCommitHook(redis_update_lobby, args=(lobby,))
