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
from lobbypy.lib.ajax_json import make_lobby_player_delta
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
