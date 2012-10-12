from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from pyramid.security import has_permission, forget, authenticated_userid

from lobbypy.resources import *
from lobbypy.resources.lobby import LobbyPlayer
from lobbypy.lib.ajax_json import make_lobby_player_delta
from bson.objectid import ObjectId

import logging

log = logging.getLogger(__name__)

@view_config(route_name='lobby_create', request_method='POST',
        permission='play')
def create_lobby(request):
    """
    Create lobby owned by current logged in player
    """
    player = request.player
    assert player is not None
    from lobbypy.resources.lobby import destroy_owned_lobbies
    destroy_owned_lobbies(player)
    params = request.POST
    name = params['name']
    # Create the lobby
    lobby = Lobby(name=name, owner=player,
                    players=[LobbyPlayer(player=player, team=0)])
    lobby.save()
    log.info('Player with id %s created a lobby with id %s' %
            (player.id, lobby.id))
    return HTTPFound(location=request.route_url('lobby', lobby_id=lobby.id))

@view_config(route_name='lobby', renderer='../templates/lobby.pt')
def view_lobby(context, request):
    """
    View lobby
    Join if logged in, otherwise just view
    """
    lobby = Lobby.objects.with_id(request.matchdict['lobby_id'])
    if has_permission('play', context, request):
        # Join the lobby if authenticated
        player = request.player
        assert player is not None
        from lobbypy.resources.lobby import (leave_lobbies,
                destroy_owned_lobbies)
        destroy_owned_lobbies(player, lobby)
        leave_lobbies(player, lobby)
        # Join the lobby if we weren't alread in the lobby
        if all(map(lambda x: x.player != player, lobby.players)):
            lobby.update(push__players = LobbyPlayer(player=player,
                    team=0))
            log.info('Player with id %s joined lobby with id %s' %
                    (player.id, lobby.id))
    master = get_renderer('../templates/master.pt').implementation()
    return dict(master=master, lobby=lobby)

@view_config(route_name='lobby_leave')
def leave_lobby(request):
    """
    Leave lobby
    Leave if only a player, destroy if owner
    """
    lobby = Lobby.objects.with_id(request.matchdict['lobby_id'])
    player = request.player
    assert player is not None
    if lobby.owner == player:
        lobby.delete()
        log.info('Lobby owner with id %s destroyed lobby with id %s' %
                (player.id, lobby.id))
    else:
        lobby.update(pull__players__player = player)
        log.info('Player with id %s left lobby with id %s' %
                (player.id, lobby.id))
    return HTTPFound(location = request.route_url('root'))
