from pyramid.security import remember

from bson.objectid import ObjectId
import re, logging, transaction

from ..models import Player, DBSession

log = logging.getLogger(__name__)

_sid_matcher = re.compile(r'http://steamcommunity\.com/openid/id/(\d+)')
def openid(context, request, openid_dict):
    """
    Do auth for user
    - if openid does not exist in db, create new Player and auth
    - else auth as existing player
    """
    steamid = int(_sid_matcher.match(openid_dict['identity_url']).group(1))
    with transaction.manager:
        player = DBSession.query(Player).filter_by(steamid=steamid).first()
        if player is None:
            # make a new one
            player = Player(steamid)
            DBSession.add(player)
            log.info('New Player with steamid %d was authenticated through Steam and created' % steamid)
        else:
            log.info('Returning Player with steamid %d authenticated through Steam' % steamid)
    player = DBSession.query(Player).filter_by(steamid=steamid).first()
    # set up session for this player
    headers = remember(request, player.steamid)
    log.info('Player[%d] logged in' % player.steamid)
    return (player, headers)

def group_lookup(user_id, request):
    player = DBSession.query(Player).filter_by(steamid=user_id).first()
    if player is not None:
        return []
    return None
