from lobbypy.resources import Player
import re
import logging

log = logging.getLogger(__name__)

_sid_matcher = re.compile(r'http://steamcommunity\.com/openid/id/(\d+)')
def openid(context, request, openid_dict):
    """
    Do auth for user
    - if openid does not exist in db, create new Player and auth
    - else auth as existing player
    """
    steamid = int(_sid_matcher.match(openid_dict['identity_url']).group(1))
    player_dict = {'steamid':steamid}
    player = Player.objects(**player_dict).first()
    if player is None:
        # make a new one
        player = Player(**player_dict)
        player.save()
        log.info('New Player with steamid %d was authenticated through Steam and created' % steamid)
    else:
        log.info('Returning Player with steamid %d authenticated through Steam' % steamid)
    # set up session for this player
    request.session['_id'] = player.id
    log.info('Player with Objectid %s logged in' % player.id)
    return player
