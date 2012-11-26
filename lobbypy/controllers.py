from sqlalchemy import event, or_, and_
from sqlalchemy.orm import joinedload
import transaction, gevent

from .models import (
        Lobby,
        Team,
        LobbyPlayer,
        PyramidJSONEncoder,
        SimpleLobbyJSONEncoder,
        DBSession,
        spectator_table,
        )
from .lib.srcds_api import check_map, check_players, connect, SRCDS

import logging

log = logging.getLogger(__name__)

def redis_update_lobby(success, lobby):
    import redis
    from json import dumps
    if success:
        r = redis.Redis()
        lobby = DBSession.merge(lobby)
        open_classes = lobby.get_open_classes()
        r.publish('lobbies', dumps(dict(event='update', lobby=lobby),
                cls=SimpleLobbyJSONEncoder))
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

def redis_start_lobby(success, lobby):
    import redis
    from json import dumps
    if success:
        r = redis.Redis()
        r.publish('lobbies', dumps(dict(event='destroy', lobby_id=lobby.id)))
        r.publish('lobby/%s' % lobby.id, dumps(dict(event='start',
                password=lobby.password)))

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
    return (all([leave(session, l, player) for l in spec_lobbies]) and
            all([leave(session, l, player) for l in player_lobbies]))

def create_lobby(session, name, player, rcon_info, game_map, init_server=True):
    """
    Create a lobby in the database
    """
    log.info('Player[%s] creating lobby' % player.steamid)
    if not leave_old_lobbies(session, player):
        return None
    # create lobby
    # TODO: grab a random password from premade list
    password = 'password'
    lobby = Lobby(name, player, rcon_info, game_map, password)
    if init_server:
        server = check_server(lobby)
        prep_server(server, lobby, password)
        server.disconnect()
    session.add(lobby)
    current = transaction.get()
    current.addAfterCommitHook(redis_create_lobby, args=(lobby,))
    return lobby

def destroy_lobby(session, lobby):
    """
    Delete a lobby from the database
    """
    if lobby.lock:
        return False
    lobby_id = lobby.id
    log.info('Destroying Lobby[%s]' % lobby_id)
    session.delete(lobby)
    current = transaction.get()
    current.addAfterCommitHook(redis_destroy_lobby, args=(lobby_id,))
    return True

def start_lobby(session, lobby):
    """
    Lock lobby, preventing changes
    """
    if lobby.is_ready():
        lobby.lock = True
        # TODO: make and add match object for this lobby
        current = transaction.get()
        current.addAfterCommitHook(redis_start_lobby, args=(lobby,))

def check_server(lobby):
    server = connect(lobby.server)
    # check the map exists on the server
    check_map(server, lobby.gmap)
    # check there are no players on the server
    check_players(server)
    # if check was successful, return the server
    return server

def prep_server(server, lobby, password):
    # change the map
    server.rcon_command('changelevel %s' % lobby.gmap)
    # reconnnect BECAUSE RCON SUCKS
    gevent.sleep(3)
    server.connect()
    # set the password
    server.rcon_command('sv_password %s' % password)
    # TODO: set the config options

def join(session, lobby, player):
    """
    Add a player to lobby
    """
    if lobby.has_player(player):
        return False
    # leave old lobbies
    if not leave_old_lobbies(session, player):
        return False
    # join lobby
    log.info('Player[%s] joinling Lobby[%s]' % (player.steamid, lobby.id))
    lobby.join(player)
    current = transaction.get()
    current.addAfterCommitHook(redis_update_lobby, args=(lobby,))
    return True

def leave(session, lobby, player):
    """
    Remove a player from lobby
    """
    if lobby.lock and (lobby.on_team(player) or player is lobby.owner):
        return False
    log.info('Player[%s] leaving Lobby[%s]' % (player.steamid, lobby.id))
    if lobby.owner is player:
        return destroy_lobby(session, lobby)
    else:
        lobby.leave(player)
        current = transaction.get()
        current.addAfterCommitHook(redis_update_lobby, args=(lobby,))
        return True

def set_team(session, lobby, player, team_id):
    """
    Set a player's team in lobby
    """
    if lobby.lock:
        return False
    if lobby.has_player(player):
        log.info('Player[%s] setting team to %s in Lobby[%s]' % (player.steamid,
                team_id, lobby.id))
        lobby.set_team(player, team_id)
        current = transaction.get()
        current.addAfterCommitHook(redis_update_lobby, args=(lobby,))
        return True
    else:
        return False

def set_class(session, lobby, player, cls):
    """
    Set a player's class in lobby
    """
    if lobby.lock:
        return False
    if lobby.on_team(player) and not lobby.get_team(player).has_class(cls):
        log.info('Player[%s] setting class to %s in Lobby[%s]' % (player.steamid,
                cls, lobby.id))
        lobby.set_class(player, cls)
        transaction.get().addAfterCommitHook(redis_update_lobby, args=(lobby,))
        return True
    else:
        return False

def toggle_ready(session, lobby, player):
    """
    Toggle a ready for a player in lobby
    """
    if lobby.lock:
        return False
    if lobby.on_team(player):
        log.info('Player[%s] toggling ready in Lobby[%s]' % (player.steamid,
                lobby.id))
        lobby.toggle_ready(player)
        transaction.get().addAfterCommitHook(redis_update_lobby, args=(lobby,))
        return True
    else:
        return False
