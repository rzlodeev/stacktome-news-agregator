from sqlalchemy import create_engine, Column, String, Text, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EntryModel(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    headline = Column(String, nullable=False)
    source_link = Column(String, nullable=False)
    date_of_publication = Column(String, nullable=False)
    title = Column(String, nullable=False)
    fulltext = Column(Text, nullable=False)
    sentiment_score = Column(Float, nullable=True)
    trend_names = Column(String, nullable=True)
