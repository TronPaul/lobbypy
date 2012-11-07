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
        elif isinstance(o, dict):
            d = dict()
            for k, v in o.items():
                d[self.default(k)] = self.default(v)
            return d
        elif isinstance(o, list):
            l = list()
            for i in o:
                l.append(self.default(i))
            return l
        elif isinstance(o, long):
            return str(o)
        else:
            return o
