#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, SessionLocal
from app.data_generator import seed_initial_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    
    db = SessionLocal()
    seed_initial_data(db, num_transactions=10000)
    db.close()
    
    logger.info("Database initialization complete!")
