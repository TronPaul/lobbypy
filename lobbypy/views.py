from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound, HTTPCreated
from pyramid.events import ContextFound
from pyramid.events import subscriber
from lobbypy import resources
from pyramid_openid.view import (process_incoming_request,
        process_provider_response)

@view_config(context=resources.root.Root, renderer='templates/root.pt')
def root_view(context, request):
    master = get_renderer('templates/master.pt').implementation()
    lobby_coll = context['lobby'].collection
    lobbies = lobby_coll.find(limit=20)
    return dict(master=master, lobbies=lobbies)

@view_config(context=resources.collections.LobbyCollection,
        request_method='POST', name='create', permission='system.Authenticated')
def create_lobby(context, request):
    lobby_coll = context.collection
    params = request.POST
    name = params['name']
    lobby_dict = dict(name=params['name'], owner=request.player._id)
    _id = lobby_coll.save(lobby_dict)
    return HTTPFound(location=request.resource_url(context[_id]))

@view_config(context=resources.collections.Lobby,
        renderer='templates/lobby.pt')
def view_lobby(context, request):
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
