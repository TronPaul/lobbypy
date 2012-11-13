from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
        )

from zope.sqlalchemy import ZopeTransactionExtension

from json import JSONEncoder

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class PyramidJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Base):
            return self.default(o.__json__(None))
        elif isinstance(o, long):
            return str(o)
        else:
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
