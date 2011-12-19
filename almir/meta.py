from pyramid.httpexceptions import exception_response
from psycogreen.gevent.psyco_gevent import make_psycopg_green
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension


def readonly_flush(*a, **kw):
    print 'readonly session, there should be no writes to DB'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
DBSession.flush = readonly_flush
Base = declarative_base()


class ModelMixin(object):
    query = DBSession.query_property()

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def objects_list(cls):
        return {'objects': cls.query}

    @classmethod
    def object_detail(cls, id_):
        obj = cls.query.get(id_)
        if obj == None:
            raise exception_response(404)
        else:
            return {'object': obj}


def initialize_sql(engine):
    # TODO: move to post_fork of gunicorn hook
    make_psycopg_green()
    DBSession.configure(bind=engine)
    Base.metadata.reflect(engine)
