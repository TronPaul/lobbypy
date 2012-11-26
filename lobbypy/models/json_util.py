from json import JSONEncoder

from . import Base, Lobby

class PyramidJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Base):
            return self.default(o.__json__(None))
        elif isinstance(o, set):
            return sorted([i for i in o])
        elif isinstance(o, long):
            return str(o)
        else:
            return o

class SimpleLobbyJSONEncoder(PyramidJSONEncoder):
    def default(self, o):
        if isinstance(o, Lobby):
            # TODO: add server info
            return {
                    'name': o.name,
                    'owner': o.owner,
                    'map': o.gmap,
                    'num_spectators': len(o.spectators),
                    'num_players': sum([len(t) for t in o.teams]),
                    'open_classes': o.get_open_classes(),
                   }
        else:
            super(SimpleLobbyJSONEncoder, self).default(o)

def simple_lobby_prep(o):
    if isinstance(o, Lobby):
        # TODO: add server info
        return simple_lobby_prep({
                'id': o.id,
                'name': o.name,
                'owner': o.owner,
                'map': o.gmap,
                'num_spectators': len(o.spectators),
                'num_players': sum([len(t) for t in o.teams]),
                'open_classes': o.get_open_classes(),
               })
    elif isinstance(o, Base):
        return simple_lobby_prep(o.__json__(None))
    elif isinstance(o, set):
        return sorted([simple_lobby_prep(i) for i in o])
    elif isinstance(o, list):
        return [simple_lobby_prep(i) for i in o]
    elif isinstance(o, dict):
        return dict([(simple_lobby_prep(k), simple_lobby_prep(v)) for
                k, v in o.items()])
    return o

def prep_json_encode(data):
    if isinstance(data, Base):
        return prep_json_encode(data.__json__(None))
    elif isinstance(data, list):
        return [prep_json_encode(i) for i in data]
    elif isinstance(data, dict):
        return dict([(prep_json_encode(k), prep_json_encode(v)) for
                k, v in data.items()])
    return data
