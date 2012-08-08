from pyramid.threadlocal import get_current_registry

import logging, json, urllib2

log = logging.getLogger(__name__)

def _get_api_key():
    return get_current_registry().settings['steam.api_key']

def _get_player_summaries_link_base():
    # TODO: format betterer
    return 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=%s&steamids=' % _get_api_key()

def _get_player_friends_link_base():
    # TODO: format betterer
    return 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=%s&steamid=' % _get_api_key()

def get_player_summary(steamid):
    """
    Get player data via Steam API GetPlayerSummaries
    """
    # TODO: error checking here
    link = '%s%s' % (_get_player_summaries_link_base(), steamid)
    return json.load(urllib2.urlopen(link))['response']['players'][0]

def get_player_friends(steamid):
    """
    Get friend list via Steam API GetFriendList
    """
    # TODO: error checking here
    return  json.load(urllib2.urlopen('%s%s' % (_get_player_friends_link_base(), steamid)))
