from sqlalchemy import create_engine, Column, String, Text, Integer, Float
from sqlalchemy.orm import sessionmaker
import logging
import traceback

from src.models import Base, EntryModel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine('sqlite:////app/data/entries.db')
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


class DB:
    def __init__(self):
        self.session = SessionLocal()
        logger.info('Database initiated')

    def add_entry(self, entry):
        self.session.add(entry)
        self.session.commit()

    def delete_all_entries(self):
        self.session.query(EntryModel).delete()
        self.session.commit()

    def get_all_entries(self):
        """Get all article entries sorted by descending order of sentiment score"""
        entries = self.session.query(EntryModel).order_by(EntryModel.sentiment_score.desc()).all()
        return entries

    def close_db(self):
        self.session.close()
