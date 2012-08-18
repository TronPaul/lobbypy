from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound, HTTPCreated
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid_openid.view import (process_incoming_request,
        process_provider_response)

from lobbypy.resources import *
from bson.objectid import ObjectId

import logging

log = logging.getLogger(__name__)

@view_config(route_name='root', renderer='templates/root.pt')
def root_view(request):
    master = get_renderer('templates/master.pt').implementation()
    lobbies = Lobby.objects[:20]
    return dict(master=master, lobbies=lobbies)

@view_config(route_name='lobby_create', request_method='POST',
        permission='system.Authenticated')
def create_lobby(request):
    from lobbypy.resources.lobby import LobbyPlayer
    params = request.POST
    name = params['name']
    lobby_dict = dict()
    lobby = Lobby(name=params['name'], owner=request.player,
                    players=[LobbyPlayer(player=request.player, team=0)])
    lobby.save()
    log.info('Player with id %s created a lobby with id %s' %
            (request.player.id, lobby.id))
    return HTTPFound(location=request.route_url('lobby', lobby_id=lobby.id))

@view_config(route_name='lobby', renderer='templates/lobby.pt')
def view_lobby(request):
    lobby_q = Lobby.objects(id=request.matchdict['lobby_id'])
    lobby = lobby_q.first()
    # Check if the player is in other lobbies, if so, remove us from them
    old_lobbies = Lobby.objects(players__player = request.player)
    rejoin = False
    for old_lobby in old_lobbies:
        if old_lobby.id != lobby.id:
            if old_lobby.owner == request.player:
                # Destroy this lobby
                # TODO: just give lobby lead to someone else?
                # TODO: kick everyone out of the lobby back to the main page
                old_lobby.delete()
                log.info('Lobby owner with id %s left lobby with id %s' %
                    (request.player.id, old_lobby.id))
            else:
                Lobby.objects(id=old_lobby.id).update_one(pull__players__player
                        = request.player)
            log.info('Player with id %s left lobby with id %s' %
                    (request.player.id, old_lobby.id))
        else:
            rejoin = True
    if not rejoin:
        from lobbypy.resources.lobby import LobbyPlayer
        lobby_q.update_one(__push__players = LobbyPlayer(player=request.player,
            team=0))
        log.info('Player with id %s joined lobby with id %s' %
                    (player_id, old_lobby._id))
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master, lobby=lobby)

@view_config(route_name='login', renderer='templates/root.pt')
def login_view(request):
    openid_mode = request.params.get('openid.mode', None)
    if openid_mode is None:
        return process_incoming_request(None, request,
                'https://steamcommunity.com/openid/')
    elif openid_mode == 'id_res':
        process_provider_response(None, request)
    return HTTPFound(location=request.route_path('root'))

@view_config(route_name='player', renderer='templates/player.pt')
def player_view(request):
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master)

@subscriber(NewRequest)
def get_player_from_session(event):
    player = None
    if '_id' in event.request.session:
        player = Player.objects(id=event.request.session['_id']).first()
    event.request.player = player
