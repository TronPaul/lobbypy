from lobbypy.resources import Player

from pyramid.security import remember

from bson.objectid import ObjectId
import re, logging

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
    headers = remember(request, str(player.id))
    log.info('Player with Objectid %s logged in' % player.id)
    return (player, headers)

def group_lookup(user_id, request):
    player = Player.objects.with_id(ObjectId(user_id))
    if player is not None:
        return []
    return None
