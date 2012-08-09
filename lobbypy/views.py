from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound, HTTPCreated
from pyramid.events import ContextFound
from pyramid.events import subscriber
from pyramid_openid.view import (process_incoming_request,
        process_provider_response)

from lobbypy import resources

from bson.objectid import ObjectId

import logging

log = logging.getLogger(__name__)

@view_config(context=resources.root.Root, renderer='templates/root.pt')
def root_view(context, request):
    master = get_renderer('templates/master.pt').implementation()
    lobbies = context['lobby'].find(limit=20)
    return dict(master=master, lobbies=lobbies)

@view_config(context=resources.collections.LobbyCollection,
        request_method='POST', name='create', permission='system.Authenticated')
def create_lobby(context, request):
    lobby_coll = context.collection
    params = request.POST
    name = params['name']
    lobby_dict = dict(name=params['name'], owner_id=request.player._id,
            players=[dict(player_id=request.player._id, team=0)])
    _id = lobby_coll.insert(lobby_dict)
    log.info('Player with id %s created a lobby with id %s' %
            (request.player._id, _id))
    return HTTPFound(location=request.resource_url(context[_id]))

@view_config(context=resources.collections.Lobby,
        renderer='templates/lobby.pt')
def view_lobby(context, request):
    # Check if the player is in other lobbies, if so, remove us from them
    lobby_coll = context.__parent__
    player_id = request.player._id
    old_lobbies = lobby_coll.find(
            **{'players':{'$elemMatch':{'player_id':player_id}}})
    for old_lobby in old_lobbies:
        if old_lobby._id != context._id:
            log.info('Player with id %s left lobby with id %s' %
                    (player_id, old_lobby._id))
            if old_lobby.owner_id == player_id:
                # Destroy this lobby
                # TODO: just give lobby lead to someone else?
                lobby_coll.remove(spec_or_id=ObjectId(old_lobby._id))
            else:
                old_lobby.players[:] = [p for p in old_lobby.players
                        if p.get('_id') != player_id]
                lobby_coll.save(**old_lobby)
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master, lobby=context)

@view_config(context=resources.root.Root, name='login', renderer='templates/root.pt')
def login_view(context, request):
    openid_mode = request.params.get('openid.mode', None)
    if openid_mode is None:
        return process_incoming_request(context, request,
                'https://steamcommunity.com/openid/')
    elif openid_mode == 'id_res':
        process_provider_response(context, request)
    return HTTPFound(location=request.resource_url(context))

@view_config(context=resources.collections.Player,
        renderer='templates/player.pt')
def player_view(context, request):
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master)

@subscriber(ContextFound)
def get_player_from_session(event):
    player = None
    if '_id' in event.request.session:
        player = event.request.root['player'][event.request.session['_id']]
    event.request.player = player
