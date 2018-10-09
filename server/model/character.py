from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from .base import Base
from .account import Account


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    account_username = Column(String, ForeignKey(Account.username))

    name = Column(String, nullable=False)

    last_x = Column(Float, nullable=False)
    last_y = Column(Float, nullable=False)
    velocity_x = Column(Float, nullable=False)
    velocity_y = Column(Float, nullable=False)
    last_position_update = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'<Character id={self.id} name={self.name}>'

    def get_position(self):
        now = datetime.now()
        delta = (now - self.last_position_update).total_seconds()
        self.last_x = self.last_x + self.velocity_x * delta
        self.last_y = self.last_y + self.velocity_y * delta
        self.last_position_update = now
        return self.last_x, self.last_y