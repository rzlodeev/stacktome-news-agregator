from fastapi import FastAPI, Depends, HTTPException
import logging
from src.database import DB
from src.models import EntryModel

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('Initiating connection to the database...')
db_instance = DB()


@app.get("/init")
def init_database_entry():
    try:
        entry_model = EntryModel(
            headline="headline",
            source_link="link",
            date_of_publication="date",
            title="title",
            fulltext="text",
            sentiment_score=0.0,
            trend_names="list"
        )
        db_instance.add_entry(entry_model)
        logger.info(f"Init entry added")
        entries = db_instance.get_all_entries()
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trending_articles")
def read_entries():
    try:
        entries = db_instance.get_all_entries()
        logger.info(f"Retrieved {len(entries)} entries from the database.")
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
