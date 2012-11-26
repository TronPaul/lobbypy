from sqlalchemy import (
        Column,
        Integer,
        )
from sqlalchemy.orm import relationship

from . import Base

class Player(Base):
    __tablename__ = 'player'
    steamid = Column(Integer, primary_key=True)
    lobby = relationship("Lobby", uselist=False, backref='owner')

    def __init__(self, steamid):
        self.steamid = steamid

    def __getattr__(self, name):
        if name == 'name':
            # Player name from steam
            return self._get_persona_name()
        elif name == 'avatar_large':
            return self._get_avatar_url('large')
        elif name == 'avatar_medium':
            return self._get_avatar_url('medium')
        elif name == 'avatar_small':
            return self._get_avatar_url()
        raise AttributeError(name)

    def __json__(self, request):
        return {
                'steamid': self.steamid,
                'name': self.name
                }

    def _get_persona_name(self):
        return self._get_player_summary()['personaname']

    def _get_avatar_url(self, size='small'):
        summary = self._get_player_summary()
        if size == 'large':
            return summary['avatarfull']
        elif size == 'medium':
            return summary['avatarmedium']
        else:
            return summary['avatar']

    # TODO: cache this
    def _get_player_summary(self):
        from ..lib import get_player_summary
        # Do Steam API call to get all data from GetPlayerSummaries for steamid
        return get_player_summary(self.steamid)
