from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EventDetails(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    event_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    ticket_capacity = Column(Integer, nullable=False)


class TicketDetails(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    metadata_ = Column("metadata", JSON)
    ticket_status = Column(Boolean, default=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
