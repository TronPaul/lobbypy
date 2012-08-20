from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound, HTTPCreated
from pyramid.events import NewRequest, NewResponse
from pyramid.events import subscriber
from pyramid_openid.view import (process_incoming_request,
        process_provider_response)
from pyramid.security import has_permission, forget, authenticated_userid

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
        permission='play')
def create_lobby(request):
    player = request.player
    assert player is not None
    from lobbypy.resources.lobby import destroy_owned_lobbies
    destroy_owned_lobbies(player)
    params = request.POST
    name = params['name']
    # Create the lobby
    lobby = Lobby(name=params['name'], owner=player,
                    players=[LobbyPlayer(player=player, team=0)])
    lobby.save()
    log.info('Player with id %s created a lobby with id %s' %
            (player.id, lobby.id))
    return HTTPFound(location=request.route_url('lobby', lobby_id=lobby.id))

@view_config(route_name='lobby', renderer='templates/lobby.pt')
def view_lobby(context, request):
    lobby = Lobby.objects(id=request.matchdict['lobby_id']).first()
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
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master, lobby=lobby)

@view_config(route_name='lobby_set_team', request_method='POST',
        renderer='json', permission='play')
def ajax_set_team(request):
    params = request.POST
    team = params['team']
    Lobby.objects(id=request.matchdict['lobby_id'], players__player =
            request.player).update(set__players__S__team = team)
    lobby = Lobby.object(id=request.matchdict['lobby_id']).only('id').first()
    log.info('Player with id %s set team to %s in lobby %s' %
            (request.player.id, team, lobby.id))
    return {'team':filter(lambda x: x == request.player, lobby.players)[0].team}

@view_config(route_name='lobby_set_class', request_method='POST',
        renderer='json', permission='play')
def ajax_set_class(request):
    params = request.POST
    pclass = params['pclass']
    Lobby.objects(id=request.matchdict['lobby_id'], players__player =
            request.player).update(set__players__S__pclass = pclass)
    lobby = Lobby.object(id=request.matchdict['lobby_id']).first()
    log.info('Player with id %s set class to %s in lobby %s' %
            (request.player.id, pclass, lobby))
    return {'team':filter(lambda x: x == request.player, lobby.players)[0].pclass}

def ajax_keep_alive(request):
    pass

@view_config(route_name='login')
def login_view(request):
    openid_mode = request.params.get('openid.mode', None)
    if openid_mode is None:
        return process_incoming_request(None, request,
                'https://steamcommunity.com/openid/')
    elif openid_mode == 'id_res':
        player, headers = process_provider_response(None, request)
    return HTTPFound(location=request.route_path('root'), headers=headers)

@view_config(route_name='logout')
def logout_view(request):
    player = request.player
    assert player is not None
    request.session.invalidate()
    headers = forget(request)
    owned_lobbies_q = Lobby.objects(owner = player)
    map(lambda x: log.info('Owner with id %s leaving Lobby with id %s' %
            (player.id, x.id)), owned_lobbies_q.all())
    owned_lobbies_q.delete(True)
    # Check if the player is in any lobbies, remove the player from them
    old_lobbies_q = Lobby.objects(players__player = player)
    map(lambda x: log.info('Player with id %s leaving Lobby with id %s' %
            (player.id, x.id)), old_lobbies_q.all())
    old_lobbies_q.update(pull__players__player = player)
    return HTTPFound(location=request.route_path('root'), headers=headers)

@view_config(route_name='player', renderer='templates/player.pt')
def player_view(request):
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master)

@subscriber(NewRequest)
def get_player_from_session(event):
    user_id = authenticated_userid(event.request)
    if user_id is not None:
        player = Player.objects.with_id(ObjectId(user_id))
        event.request.player = player
    elif hasattr(event.request, 'player'):
        del event.request.player
