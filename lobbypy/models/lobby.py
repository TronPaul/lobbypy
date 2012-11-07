from sqlalchemy import (
        Column,
        Integer,
        String,
        ForeignKey,
        Table
        )

from sqlalchemy.orm import relationship
from sqlalchemy.event import listens_for

from . import Base, PyramidJSONEncoder

spectator_table = Table('spectator', Base.metadata,
        Column('lobby_id', Integer, ForeignKey('lobby.id'), primary_key=True),
        Column('player_id', Integer, ForeignKey('player.steamid'),
            primary_key=True),
        )

class Lobby(Base):
    __tablename__ = 'lobby'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('player.steamid'), nullable=False)
    teams = relationship("Team", backref="lobby",
            cascade='save-update,merge,delete')
    spectators = relationship("Player", secondary=spectator_table)

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.join(owner)
        self.teams.append(Team('Red'))
        self.teams.append(Team('Blue'))

    def __len__(self):
        return len(spectators) + sum([len(t) for t in self.teams])

    def __json__(self, request):
        return {
                'id': self.id,
                'name': self.name,
                'owner': self.owner,
                'teams': self.teams,
                'spectators': self.spectators,
                }

    def has_player(self, player):
        return (any([s is player for s in self.spectators]) or
                any([t.has_player(player) for t in self.teams]))

    def join(self, player):
        if not self.has_player(player):
            self.spectators.append(player)
        else:
            raise ValueError('%s already in %s' % (player, self))

    def leave(self, player):
        if player is self.owner:
            raise ValueError('%s is %s\'s owner' % (player, self))
        if player in self.spectators:
            self.spectators.remove(player)
        else:
            # Don't care if the DB is insane, just remove the player
            l = [t.remove_player(player) for t in self.teams if t.has_player(player)]
            if len(l) == 0:
                raise ValueError('%s is not in %s' % (player, self))

    def set_team(self, player, team):
        if any([s.steamid == player.steamid for s in self.spectators]) and team is not None:
            self.spectators.remove(player)
            team.append_player(player)
        else:
            old_teams = [t for t in self.teams if t.has_player(player)]
            # Player found in a single team
            if len(old_teams) == 1:
                old_team = old_teams.pop()
                if team is not None and old_team is not team:
                    team.append(old_team.pop_player(player))
                else:
                    self.spectators.append(player)
            # Player not found
            elif len(old_teams) == 0:
                raise ValueError('%s not in %s' % (player, self))
            # Should only be one player per team.
            # BAD THINGS IN DB LAND
            else:
                pass

    def set_class(self, player, cls):
        teams = [t for t in self.teams if t.has_player(player)]
        # Player found in a single team
        if len(teams) == 1:
            teams.pop().set_class(player, cls)
        # Player not found
        elif len(teams) == 0:
            raise ValueError('%s not in %s' % (player, self.teams))
        # Should only be one player per team.
        # BAD THINGS IN DB LAND
        else:
            # TODO: error
            pass

class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    lobby_id = Column(Integer, ForeignKey('lobby.id'), nullable=False)
    players = relationship("LobbyPlayer", backref="team",
            cascade='save-update,merge,delete')

    def __init__(self, name):
        self.name = name

    def __len__(self):
        return len(players)

    def __json__(self, request):
        return {
                'name': self.name,
                'players': self.players,
                }

    def has_player(self, player):
        return len([lp for lp in self.players
                if lp.player is player]) > 0

    def get_player(self, player):
        return [lp for lp in self.players if lp.player is player].pop()

    def append(self, lobby_player):
        self.players.append(lobby_player)

    def remove(self, lobby_player):
        self.players.remove(lobby_player)

    def append_player(self, player):
        lp = LobbyPlayer(player)
        self.append(lp)

    def pop_player(self, player):
        lps = [lp for lp in self.players if lp.player is player]
        if len(lps) == 1:
            lp = lps.pop()
            self.remove(lp)
            return lp
        elif len(lps) == 0:
            raise ValueError('%s not in %s' % (player, self.players))
        else:
            # TODO: error
            pass

    def remove_player(self, player):
        lps = [lp for lp in self.players if lp.player is player]
        if len(lps) == 1:
            lp = lps.pop()
            self.remove(lp)
        elif len(lps) == 0:
            raise ValueError('%s not in %s' % (player, self.players))
        else:
            # TODO: error
            pass

    def set_class(self, player, cls):
        if cls is not None and (cls < 1 or cls > 9):
            raise ValueError('%s is a bad class' % cls)
        elif cls is not None and len([lp for lp in self.players if lp.cls ==
                cls]) > 0:
            raise ValueError('Class %s is already taken' % cls)
        lps = [lp for lp in self.players if lp.player is player]
        if len(lps) == 1:
            lp = lps.pop()
            # Set the class if no one else has it
            lp.cls = cls
            # TODO: check to make sure others don't have that class
        elif len(lps) == 0:
            raise ValueError('%s not in %s' % (player, self.players))
        else:
            # TODO: error
            pass

class LobbyPlayer(Base):
    __tablename__ = 'lobby_player'
    team_id = Column(Integer, ForeignKey('team.id'), primary_key=True)
    player_id = Column(Integer, ForeignKey('player.steamid'), primary_key=True)
    player = relationship("Player", uselist=False)
    cls = Column(Integer)

    def __init__(self, player, cls=None):
        self.player = player
        self.cls = cls

    def __json__(self, request):
        return {
                'player': self.player,
                'class': self.cls,
                }
