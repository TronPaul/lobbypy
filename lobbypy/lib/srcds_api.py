from . import SRCDS

def connect(rcon_info):
    rcon_pass, rcon_server_port = rcon_info.split('@')
    rcon_server, rcon_port = rcon_server_port.split(':')
    return SRCDS(rcon_server, int(rcon_port), rcon_pass)

def check_map(server, game_map):
    """
    Check that the given map exists on the server
    """
    resp = server.rcon_command('maps %s.bsp' % game_map)
    if resp == '':
        raise ValueError('Server at %s:%d does not have any maps matching %s' %
                (server.ip, server.port, lobby.gmap))
    i = resp.find('PENDING')
    if i == -1:
        raise ValueError('The response from server at %s:%d was not \
                empty, but did not have PENDING.  This should never happen!' %
                (server.ip, server.port))
    elif resp.find('PENDING', i+1) != -1:
        raise ValueError('Server at %s:%d had multiple maps matching %s' %
                (server.ip, server.port, lobby.gmap))
    return True

def check_players(server, bots=True):
    """
    Check that there are no players on the server
    If bots is false, bots count as players
    """
    return True
