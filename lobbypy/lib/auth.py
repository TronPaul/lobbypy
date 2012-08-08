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
    player_coll = context['player'].collection
    player_dict = {'steamid':steamid}
    player = player_coll.find_one(player_dict)
    if player is None:
        # make a new one
        player_coll.save(player_dict)
        log.info('New Player with steamid %d was authenticated through Steam and created' % steamid)
        player = player_coll.find_one(player_dict)
    else:
        log.info('Returning Player with steamid %d authenticated through Steam' % steamid)
    # set up session for this player
    request.session['_id'] = player['_id']
    log.info('Player with Objectid %s logged in' % player['_id'])
    return player
