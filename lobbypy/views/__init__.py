from pyramid.httpexceptions import HTTPFound
from pyramid_openid.view import (process_incoming_request,
        process_provider_response)
from pyramid.security import forget, authenticated_userid

from ..models import (
        DBSession,
        Player
        )

from .ajax_lobby import (
        create_lobby_ajax,
        all_lobbies_ajax,
        lobby_state_ajax,
        )

__all__ = [
        'index',
        'login',
        'logout',
        'create_lobby_ajax',
        'all_lobbies_ajax',
        'lobby_state_ajax',
        ]

import logging

log = logging.getLogger(__name__)

def index(request):
    """
    Root view for lobbypy
    """
    user_id = authenticated_userid(request)
    player = None
    if user_id is not None:
        player = DBSession.query(Player).filter(Player.steamid==user_id).first()
    return dict(player=player)

def login(request):
    """
    Login through Steam
    """
    openid_mode = request.params.get('openid.mode', None)
    if openid_mode is None:
        return process_incoming_request(None, request,
                'https://steamcommunity.com/openid/')
    elif openid_mode == 'id_res':
        headers = process_provider_response(None, request)[1]
    return HTTPFound(location=request.route_path('index'), headers=headers)

def logout(request):
    """
    Logout
    clear headers/session
    """
    request.session.invalidate()
    headers = forget(request)
    return HTTPFound(location=request.route_path('index'), headers=headers)
