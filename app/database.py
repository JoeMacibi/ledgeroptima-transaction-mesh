from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from app.config import settings
from app.models import Base

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    echo=settings.debug,
)


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("SET application_name = 'telemetry_dashboard'")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
