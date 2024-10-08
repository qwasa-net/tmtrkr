"""Database models mixins and globals."""

from datetime import datetime

from sqlalchemy import TIMESTAMP, Column
from sqlalchemy.orm import declarative_base


class BaseModel:
    """BaseModel with some sugar for queries and encoders."""

    @classmethod
    def query(cls, session, **kwargs):
        q = session.query(cls)
        if kwargs:
            q = q.filter_by(**kwargs)
        return q

    @classmethod
    def first(cls, session, **kwargs):
        return cls.query(session, **kwargs).first()

    @classmethod
    def one(cls, session, **kwargs):
        return cls.query(session, **kwargs).one_or_none()

    @classmethod
    def all(cls, session, **kwargs):
        return cls.query(session, **kwargs).all()

    @classmethod
    def get_or_create(cls, session, **kwargs):
        obj = cls.first(session, **kwargs)
        if obj:
            return obj
        obj = cls(**kwargs)
        obj.save(session)
        return obj

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._columns_update:
                setattr(self, key, value)
        return self

    def as_dict(self):
        result = {}
        for key in self._columns_as_dict:
            result[key] = getattr(self, key)
        return result

    @property
    def _columns(self):
        return self.__mapper__.c.keys()

    _columns_update = _columns
    _columns_as_dict = _columns

    def save(self, session):
        session.add(self)
        session.commit()
        session.flush()
        return self


#
Base = declarative_base(cls=BaseModel)


class AutoTimestampsMixin:
    """Common mixin for timestamps."""

    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
