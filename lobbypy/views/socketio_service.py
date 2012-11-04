from socketio import socketio_manage
from lobbypy.views.socketio_lobbies import LobbiesNamespace
from lobbypy.views.socketio_lobby import LobbyNamespace

def is_socket_for(socket, player):
    s = socket.session
    return 'player' in s and s['player'] is player

def socketio_service(request):
    retval = socketio_manage(request.environ,
            {
                '/lobbies': LobbiesNamespace,
                '/lobby': LobbyNamespace
            }, request=request
    )
    return retval
