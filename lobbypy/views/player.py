from pyramid.view import view_config
from pyramid.renderers import get_renderer
from lobbypy.resources import *

import logging

log = logging.getLogger(__name__)

@view_config(route_name='player', renderer='../templates/player.pt')
def player_view(request):
    """
    View a player
    """
    master = get_renderer('../templates/master.pt').implementation()
    return dict(master=master)
