from sqlalchemy import (
        Column,
        Integer,
        String,
        ForeignKey,
        Table,
        Boolean,
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
    owner_id = Column(Integer, ForeignKey('player.steamid'), nullable=False,
            unique=True)
    teams = relationship("Team", backref="lobby",
            cascade='save-update,merge,delete')
    spectators = relationship("Player", secondary=spectator_table)
    lock = Column(Boolean, nullable=False, default=False)

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.join(owner)
        self.teams.append(Team('Red'))
        self.teams.append(Team('Blue'))

    def __len__(self):
        """
        Return the number of players in the Lobby
        """
        return len(self.spectators) + sum([len(t) for t in self.teams])

    def __json__(self, request):
        """
        Return a json version of the Lobby
        """
        return {
                'id': self.id,
                'name': self.name,
                'owner': self.owner,
                'teams': self.teams,
                'spectators': self.spectators,
                'lock': self.lock,
                'is_ready': self.is_ready(),
                }

    def is_ready(self):
        """
        Return if the Lobby ready to be started
        """
        return all([len(t) == 9 for t in self.teams])

    def has_player(self, player):
        """
        Return if the Lobby has the Player in it
        """
        return (any([s is player for s in self.spectators]) or
                any([t.has_player(player) for t in self.teams]))

    def on_team(self, player):
        """
        Return if the Player is on a team in the Lobby
        """
        return any([t.has_player(player) for t in self.teams])

    def get_team(self, player):
        """
        Return the Team the Player is on in the Lobby
        """
        teams = [t for t in self.teams if t.has_player(player)]
        if len(teams) == 1:
            return teams.pop()
        elif len(teams) == 0:
            raise ValueError('%s does not exist in %s' % (player, self.teams))
        else:
            raise ValueError('Multiple %s in %s' % (player, self.teams))

    def is_ready_player(self, player):
        """
        Return if the Player is ready in the Lobby
        """
        team = self.get_team(player)
        return team.is_ready_player(player)

    def join(self, player):
        """
        Add the Player to the Lobby (spectators list)
        """
        if not self.has_player(player):
            self.spectators.append(player)
        else:
            raise ValueError('%s already in %s' % (player, self))

    def leave(self, player):
        """
        Remove the Player from the Lobby (wherever they may be)
        """
        if player is self.owner:
            raise ValueError('%s is %s\'s owner' % (player, self))
        if player in self.spectators:
            self.spectators.remove(player)
        else:
            # Don't care if the DB is insane, just remove the player
            l = [t.remove_player(player) for t in self.teams if t.has_player(player)]
            if len(l) == 0:
                raise ValueError('%s is not in %s' % (player, self))

    def set_team(self, player, team_num):
        """
        Move the Player to or from the Team in the Lobby
        """
        if team_num is not None and player in self.spectators:
            self.spectators.remove(player)
            team = self.teams[team_num]
            team.append_player(player)
        else:
            old_team = self.get_team(player)
            if team_num is None:
                old_team.remove_player(player)
                self.spectators.append(player)
            elif old_team is not self.teams[team_num]:
                lp = old_team.pop_player(player)
                self.teams[team_num].append(lp)

    def set_class(self, player, cls):
        """
        Set the Player's class in the Lobby
        """
        team = self.get_team(player)
        team.set_class(player, cls)

    def toggle_ready(self, player):
        """
        Toggle's the Player's ready state in the Lobby
        """
        team = self.get_team(player)
        team.toggle_ready(player)

class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    lobby_id = Column(Integer, ForeignKey('lobby.id'), nullable=False)
    players = relationship("LobbyPlayer", backref="team",
            cascade='save-update,merge,delete,delete-orphan')

    def __init__(self, name):
        self.name = name

    def __len__(self):
        """
        Return the number of players in the Team
        """
        return len(self.players)

    def __json__(self, request):
        """
        Return a json version of the Team
        """
        return {
                'name': self.name,
                'players': self.players,
                }

    def has_player(self, player):
        """
        Return if the Team has the Player in it
        """
        return len([lp for lp in self.players
                if lp.player is player]) > 0

    def has_class(self, cls):
        """
        Return if the Team has a LobbyPlayer with the class
        """
        return len([lp for lp in self.players
                if lp.cls is cls]) > 0

    def get_player(self, player):
        """
        Return the LobbyPlayer that has the Player
        """
        lps = [lp for lp in self.players if lp.player is player]
        if len(lps) == 1:
            return lps.pop()
        elif len(lps) == 0:
            raise ValueError('%s not in %s' % (player, self.players))
        else:
            raise ValueError('Mulptiple %s in %s' % (player, self.players))

    def append(self, lobby_player):
        """
        Add the LobbyPlayer to the Team
        """
        if len(self.players) < 9:
            self.players.append(lobby_player)
        else:
            raise ValueError('%s\'s players list is full' % self)

    def remove(self, lobby_player):
        """
        Remove the LobbyPlayer from the Team
        """
        self.players.remove(lobby_player)

    def append_player(self, player):
        """
        Add the Player to the Team
        """
        lp = LobbyPlayer(player)
        self.append(lp)

    def pop_player(self, player):
        """
        Remove and return the LobbyPlayer with the Player from the Team
        """
        lps = [lp for lp in self.players if lp.player is player]
        if len(lps) == 1:
            lp = lps.pop()
            self.remove(lp)
            return lp
        elif len(lps) == 0:
            raise ValueError('%s not in %s' % (player, self.players))
        else:
            raise ValueError('Mulptiple %s in %s' % (player, self.players))

    def remove_player(self, player):
        """
        Remove the LobbyPlayer with the Player from the Team
        """
        lps = [lp for lp in self.players if lp.player is player]
        if len(lps) == 1:
            lp = lps.pop()
            self.remove(lp)
        elif len(lps) == 0:
            raise ValueError('%s not in %s' % (player, self.players))
        else:
            raise ValueError('Mulptiple %s in %s' % (player, self.players))

    def is_ready_player(self, player):
        """
        Return if the Player is ready in the Team
        """
        return self.get_player(player).ready

    def set_class(self, player, cls):
        """
        Set the class for the Player in the Team
        """
        if cls is not None and (cls < 1 or cls > 9):
            raise ValueError('%s is a bad class' % cls)
        elif cls is not None and len([lp for lp in self.players if lp.cls ==
                cls]) > 0:
            raise ValueError('Class %s is already taken' % cls)
        lp = self.get_player(player)
        lp.cls = cls

    def toggle_ready(self, player):
        """
        Toggle the ready state for the Player
        """
        lp = self.get_player(player)
        lp.ready = not lp.ready

class LobbyPlayer(Base):
    __tablename__ = 'lobby_player'
    team_id = Column(Integer, ForeignKey('team.id'), primary_key=True)
    player_id = Column(Integer, ForeignKey('player.steamid'), primary_key=True)
    player = relationship("Player", uselist=False)
    cls = Column(Integer)
    ready = Column(Boolean, default=False, nullable=False)

    def __init__(self, player, cls=None):
        self.player = player
        self.cls = cls

    def __json__(self, request):
        """
        Return a json version of the LobbyPlayer
        """
        return {
                'player': self.player,
                'class': self.cls,
                'ready': self.ready,
                }
