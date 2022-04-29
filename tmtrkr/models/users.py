"""User database model."""
from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship

from .base import AutoTimestampsMixin, Base


class User(Base, AutoTimestampsMixin):
    """User model."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, index=True)

    records = relationship("Record", back_populates="user")

    def __repr__(self):
        """."""
        return f"User(id={self.id!r}, name={self.name!r})"
