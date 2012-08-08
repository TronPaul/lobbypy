from pyramid.view import view_config
from lobbypy import resources
from pyramid_openid.view import process_incoming_request, process_provider_response

@view_config(context=resources.root.Root)
def root_view(context, request):
    return {'project':'lobbypy'}

@view_config(context=resources.root.Root, name='login')
def login_view(context, request):
    openid_mode = request.params.get('openid.mode', None)
    if openid_mode is None:
        return process_incoming_request(context, request,
                'https://steamcommunity.com/openid/')
    elif openid_mode == 'id_res':
        process_provider_response(context, request)
    return None
