import transaction

from pyramid.security import authenticated_userid
from sqlalchemy.orm import joinedload_all

from ..models import DBSession, Lobby, Player, Team, LobbyPlayer
from .. import controllers

import logging

log = logging.getLogger(__name__)

def create_lobby_ajax(request, init_server=True):
    """
    Player requests lobby creation
    Params:
    - name
    - rcon_pass
    - rcon_server_port
    Returns:
    - A Lobby id
    """
    name = request.params['name']
    rcon_pass = request.params['rcon_pass']
    rcon_server_port = request.params['rcon_server']
    game_map = request.params['game_map']
    user_id = authenticated_userid(request)
    if user_id is not None:
        log.info('Player[%s] posted create_lobby_ajax(%s)' % (user_id, name))
        with transaction.manager:
            player = DBSession.query(Player).filter(Player.steamid==user_id).first()
            lobby = controllers.create_lobby(DBSession, name, player, '%s@%s' %
                    (rcon_pass, rcon_server_port), game_map, init_server)
            if lobby is None:
                # TODO: return error code
                return
            transaction.commit()
            lobby = DBSession.merge(lobby)
            return lobby.id

def all_lobbies_ajax(request):
    """
    Player requests all lobby infos
    Params:
    - NONE
    Returns:
    - A list of small lobby objects
    """
    lobbies = DBSession.query(Lobby).options(
            joinedload_all(Lobby.owner),
            joinedload_all(Lobby.teams, Team.players,
                    LobbyPlayer.player),
            joinedload_all(Lobby.spectators)
            ).all()
    return lobbies

def lobby_state_ajax(request):
    """
    Player requests lobby state
    Params:
    - lobby_id
    Returns:
    - A full lobby object
    """
    lobby_id = int(request.matchdict['lobby_id'])
    lobby = DBSession.query(Lobby).filter(Lobby.id==lobby_id).options(
            joinedload_all(Lobby.owner),
            joinedload_all(Lobby.teams, Team.players,
                    LobbyPlayer.player),
            joinedload_all(Lobby.spectators)
            ).first()
    return lobby
