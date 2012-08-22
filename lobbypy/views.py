from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from pyramid.events import NewRequest
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
    """
    Root view for lobbypy
    """
    master = get_renderer('templates/master.pt').implementation()
    lobbies = Lobby.objects[:20]
    return dict(master=master, lobbies=lobbies)

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

@view_config(route_name='lobby', renderer='templates/lobby.pt')
def view_lobby(context, request):
    """
    View lobby
    Join if logged in, otherwise just view
    """
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
    """
    Set the team for the current logged in player via ajax
    """
    params = request.POST
    team = params['team']
    Lobby.objects(id=request.matchdict['lobby_id'], players__player =
            request.player).update(set__players__S__team = team)
    lobby = Lobby.objects.with_id(request.matchdict['lobby_id'])
    log.info('Player with id %s set team to %s in lobby with id %s' %
            (request.player.id, team, lobby.id))
    return {'modified':{str(request.player.id):{'team':filter(
            lambda x: x.player == request.player,
            lobby.players)[0].team}}, 'removed':[]}

@view_config(route_name='lobby_set_class', request_method='POST',
        renderer='json', permission='play')
def ajax_set_class(request):
    """
    Set the class for the current logged in player via ajax
    """
    params = request.POST
    pclass = params['class']
    Lobby.objects(id=request.matchdict['lobby_id'], players__player =
            request.player).update(set__players__S__pclass = pclass)
    lobby = Lobby.objects.with_id(request.matchdict['lobby_id'])
    log.info('Player with id %s set class to %s in lobby with id %s' %
            (request.player.id, pclass, lobby.id))
    return {'modified':{str(request.player.id):{'class':filter(
            lambda x: x.player == request.player,
            lobby.players)[0].pclass}}, 'removed':[]}

@view_config(route_name='lobby_get_players_delta', renderer='json',
        request_method='POST')
def ajex_get_players_delta(request):
    """
    Get the delta of current state of the lobby to the new state of the lobby
    """
    old_players_state = request.json_body
    # TODO: make this be a keepalive for player
    lobby = Lobby.objects.with_id(request.matchdict['lobby_id'])
    # convert client json to LobbyPlayer
    def state_to_lobby_player(s_id, inner_dict):
        """
        Convert state (key, value) pair to LobbyPlayer object
        """
        id = ObjectId(s_id)
        player = Player.objects.with_id(id)
        team = inner_dict['team']
        pclass = inner_dict['class']
        return LobbyPlayer(player=player, team=team, pclass=pclass)
    old_lobby_players = map(lambda x: state_to_lobby_player(*x),
            old_players_state.items())
    delta_dict = {}
    delta_dict['modified'] = set(lobby.players) - set(old_lobby_players)
    delta_dict['removed'] = (set(map(lambda x: x.player, old_lobby_players)) -
                             set(map(lambda x: x.player, lobby.players)))
    json_dict = {}
    json_dict['modified'] = dict(map(lambda x: (str(x.player.id),
            {'class':x.pclass, 'team':x.team}), delta_dict['modified']))
    json_dict['removed'] = map(lambda x: str(x.player.id),
            delta_dict['removed'])
    return json_dict

@view_config(route_name='login')
def login_view(request):
    """
    Login through Steam
    """
    openid_mode = request.params.get('openid.mode', None)
    if openid_mode is None:
        return process_incoming_request(None, request,
                'https://steamcommunity.com/openid/')
    elif openid_mode == 'id_res':
        headers = process_provider_response(None, request)[1]
    return HTTPFound(location=request.route_path('root'), headers=headers)

@view_config(route_name='logout')
def logout_view(request):
    """
    Logout
    clear headers/session
    """
    player = request.player
    assert player is not None
    request.session.invalidate()
    headers = forget(request)
    from lobbypy.resources.lobby import (leave_lobbies,
            destroy_owned_lobbies)
    destroy_owned_lobbies(player)
    leave_lobbies(player)
    return HTTPFound(location=request.route_path('root'), headers=headers)

@view_config(route_name='player', renderer='templates/player.pt')
def player_view(request):
    """
    View a player
    """
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master)

@subscriber(NewRequest)
def get_player_from_session(event):
    """
    Add player to request for convienence
    """
    user_id = authenticated_userid(event.request)
    if user_id is not None:
        player = Player.objects.with_id(ObjectId(user_id))
        event.request.player = player
    elif hasattr(event.request, 'player'):
        del event.request.player
