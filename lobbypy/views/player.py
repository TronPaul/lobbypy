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

@view_config(route_name='player', renderer='templates/player.pt')
def player_view(request):
    """
    View a player
    """
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master)
