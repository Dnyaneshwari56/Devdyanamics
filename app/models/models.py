from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    event_type = Column(String, nullable=False)

    weather = relationship("WeatherAnalysis", back_populates="event", uselist=False)

class WeatherAnalysis(Base):
    __tablename__ = "weather_analysis"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    temperature = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    weather_description = Column(String)
    score = Column(Integer)
    status = Column(String)

    event = relationship("Event", back_populates="weather")
