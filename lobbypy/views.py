from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound, HTTPCreated
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid_openid.view import (process_incoming_request,
        process_provider_response)

from lobbypy.resources import *
from lobbypy.resources.lobby import LobbyPlayer
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
    # Check if the player is an owner of any lobbies, destroy them
    owned_lobbies_q = Lobby.objects(owner = request.player)
    map(lambda x: log.info('Owner with id %s leaving Lobby with id %s' %
        (request.player.id, x.id)), owned_lobbies_q.all())
    owned_lobbies_q.delete(True)
    # Create the lobby
    lobby = Lobby(name=params['name'], owner=request.player,
                    players=[LobbyPlayer(player=request.player, team=0)])
    lobby.save()
    log.info('Player with id %s created a lobby with id %s' %
            (request.player.id, lobby.id))
    return HTTPFound(location=request.route_url('lobby', lobby_id=lobby.id))

@view_config(route_name='lobby', renderer='templates/lobby.pt')
def view_lobby(request):
    lobby = Lobby.objects(id=request.matchdict['lobby_id']).first()
    # Check if the player is an owner of any lobbies, destroy them
    owned_lobbies_q = Lobby.objects(owner = request.player, id__ne = lobby.id)
    map(lambda x: log.info('Owner with id %s leaving Lobby with id %s' %
        (request.player.id, x.id)), owned_lobbies_q.all())
    owned_lobbies_q.delete(True)
    # Check if the player is in any lobbies, remove the player from them
    old_lobbies_q = Lobby.objects(players__player = request.player, id__ne =
            lobby.id)
    map(lambda x: log.info('Player with id %s leaving Lobby with id %s' %
        (request.player.id, x.id)), old_lobbies_q.all())
    old_lobbies_q.update(pull__players__player = request.player)
    # Join the lobby if we weren't alread in the lobby
    if all(map(lambda x: x.player != request.player, lobby.players)):
        lobby.update(push__players = LobbyPlayer(player=request.player,
            team=0))
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master, lobby=lobby)

@view_config(route_name='lobby_set_team', request_method='POST')
def ajax_set_team(request):
    pass

@view_config(route_name='lobby_set_class', request_method='POST')
def ajax_set_class(request):
    pass

@view_config(route_name='login')
def login_view(request):
    openid_mode = request.params.get('openid.mode', None)
    if openid_mode is None:
        return process_incoming_request(None, request,
                'https://steamcommunity.com/openid/')
    elif openid_mode == 'id_res':
        process_provider_response(None, request)
    return HTTPFound(location=request.route_path('root'))

@view_config(route_name='logout')
def logout_view(request):
    player = request.player
    request.session.invalidate()
    # TODO: drop player from all lobbies
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
