from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.httpexceptions import HTTPFound
from lobbypy import resources
from pyramid_openid.view import process_incoming_request, process_provider_response

@view_config(context=resources.root.Root, renderer='templates/root.pt')
def root_view(context, request):
    player = None
    if '_id' in request.session:
        player = context['player'].collection.find_one(request.session['_id'])
    master = get_renderer('templates/master.pt').implementation()
    return dict(master=master, player=player)

@view_config(context=resources.root.Root, name='login', renderer='templates/root.pt')
def login_view(context, request):
    openid_mode = request.params.get('openid.mode', None)
    if openid_mode is None:
        return process_incoming_request(context, request,
                'https://steamcommunity.com/openid/')
    elif openid_mode == 'id_res':
        process_provider_response(context, request)
    return HTTPFound(location=request.resource_url(context))
