"""Records database model."""
from datetime import datetime
from typing import Optional

# from sqlalchemy import ARRAY, TIMESTAMP
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .base import AutoTimestampsMixin, Base


class Record(Base, AutoTimestampsMixin):
    """
    Record in the Time Tracker table.

    NB:
    Integers are used for start/end timestamps (epoch seconds).
    Tags is just a text field, not an array or M2M relation.
    """

    __tablename__ = "record"

    TAGS_DATATYPE = Text  # ARRAY(Text)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    is_deleted = Column(Boolean, default=False)
    start = Column(Integer, nullable=True)
    end = Column(Integer, nullable=True)
    name = Column(Text)
    tags = Column(TAGS_DATATYPE)

    user = relationship("User", back_populates="records")

    def __repr__(self) -> str:
        """."""
        return (
            f"Record(id={self.id!r}, user={self.user!r}, "
            f"is_deleted={self.is_deeleted!r}, "
            f"start={self.start!r}, end={self.end!r}, "
            f"name={self.name!r}, tags={self.tags!r}"
        )

    @property
    def duration(self) -> Optional[float]:
        """
        Calculate record duration in seconds.

        Returns:
        - None for not finished future records.
        - seconds since the start till the current moment
        for not finished records started in the past.
        """
        now = datetime.now().timestamp()
        end = self.end or now
        if not self.start or (self.start > max(now, end)):
            return None
        return end - self.start

    @property
    def _columns_as_dict(self) -> list:
        return self.__mapper__.c.keys() + [
            "duration",
        ]
