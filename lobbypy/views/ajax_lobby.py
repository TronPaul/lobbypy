import transaction

from pyramid.security import authenticated_userid

from ..models import DBSession, Lobby, Player
from .. import controllers

import logging

log = logging.getLogger(__name__)

def create_lobby_ajax(request):
    """
    Player requests lobby creation
    Params:
    - name
    Returns:
    - A Lobby id
    """
    name = request.params['name']
    user_id = authenticated_userid(request)
    with transaction.manager:
        player = DBSession.query(Player).filter(Player.steamid==user_id).first()
        lobby = controllers.create_lobby(DBSession, name, player)
        transaction.commit()
        lobby = DBSession.merge(lobby)
        return dict(lobby_id=lobby.id)

def all_lobbies_ajax(request):
    """
    Player requests all lobby infos
    Params:
    - NONE
    Returns:
    - A list of small lobby objects
    """
    lobbies = DBSession.query(Lobby).all()
    return dict(lobbies=lobbies)

def lobby_state_ajax(request):
    """
    Player requests lobby state
    Params:
    - lobby_id
    Returns:
    - A full lobby object
    """
    lobby_id = int(request.matchdict['lobby_id'])
    lobby = DBSession.query(Lobby).filter(Lobby.id==lobby_id).first()
    return dict(lobby=lobby)
