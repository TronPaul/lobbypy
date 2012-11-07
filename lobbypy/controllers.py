from sqlalchemy import event
import transaction

from .models import (
        Lobby,
        Team,
        LobbyPlayer,
        PyramidJSONEncoder,
        DBSession
        )

def redis_update_lobby(success, lobby):
    import redis
    from json import dumps
    if success:
        r = redis.Redis()
        lobby = DBSession.merge(lobby)
        r.publish('lobbies', dumps(dict(event='update', lobby=lobby),
                cls=PyramidJSONEncoder))
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
        r.publish('lobby/%s' % lobby_id, dumps(dict(event='destroy')))

def leave_old_lobbies(session, player):
    old_lobbies = session.query(Lobby).filter(
            Lobby.id == Team.lobby_id,
            LobbyPlayer.team_id == Team.id,
            LobbyPlayer.player_id == player.steamid).all()
    [leave(session, l, player) for l in old_lobbies]

def create_lobby(session, name, player):
    # leave old lobbies
    leave_old_lobbies(session, player)
    # create lobby
    lobby = Lobby(name, player)
    session.add(lobby)
    current = transaction.get()
    current.addAfterCommitHook(redis_create_lobby, args=(lobby,))
    return lobby

def destroy_lobby(session, lobby):
    lobby_id = lobby.id
    session.delete(lobby)
    current = transaction.get()
    current.addAfterCommitHook(redis_destroy_lobby, args=(lobby_id,))

def join(session, lobby, player):
    if lobby.has_player(player):
        return
    # leave old lobbies
    leave_old_lobbies(session, player)
    # join lobby
    lobby.join(player)
    current = transaction.get()
    current.addAfterCommitHook(redis_update_lobby, args=(lobby,))

def leave(session, lobby, player):
    if lobby.owner is player:
        destroy_lobby(session, lobby)
    else:
        lobby.leave(player)
        current = transaction.get()
        current.addAfterCommitHook(redis_update_lobby, args=(lobby,))

def set_team(session, lobby, player, team_id):
    current = transaction.get()
    player = session.merge(player)
    if team_id is not None and player in lobby.spectators:
        lobby.spectators.remove(player)
        team = lobby.teams[team_id]
        team.append_player(player)
        current.addAfterCommitHook(redis_update_lobby, args=(lobby,))
    else:
        old_team = [t for t in lobby.teams
                if t.has_player(player)].pop()
        if team_id is None:
            old_team.remove_player(player)
            lobby.spectators.append(player)
            current.addAfterCommitHook(redis_update_lobby, args=(lobby,))
        else:
            new_team = lobby.teams[team_id]
            if old_team is not new_team:
                old_lp = old_team.pop_player(player)
                new_team.append(old_lp)
                current.addAfterCommitHook(redis_update_lobby, args=(lobby,))

def set_class(session, lobby, player, cls):
    player = session.merge(player)
    team = [t for t in lobby.teams
            if t.has_player(player)].pop()
    team.set_class(player, cls)
    current = transaction.get()
    current.addAfterCommitHook(redis_update_lobby, args=(lobby,))
