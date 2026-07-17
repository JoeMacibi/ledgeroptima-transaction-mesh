import asyncio
import logging
from datetime import datetime
from threading import Thread
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.data_generator import generate_batch
from app.anomaly_detection import run_anomaly_detection
from app.config import settings

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            logger.warning("Background tasks already running")
            return
        
        self.running = True
        self.thread = Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Background tasks started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Background tasks stopped")

    def _run_loop(self):
        data_gen_interval = 5
        anomaly_check_interval = 300
        last_data_gen = 0
        last_anomaly_check = 0

        while self.running:
            current_time = datetime.utcnow().timestamp()

            if current_time - last_data_gen >= data_gen_interval:
                try:
                    db = SessionLocal()
                    generate_batch(db, batch_size=settings.synthetic_data_rate)
                    db.close()
                    last_data_gen = current_time
                except Exception as e:
                    logger.error(f"Error generating data: {str(e)}")

            if current_time - last_anomaly_check >= anomaly_check_interval:
                try:
                    db = SessionLocal()
                    run_anomaly_detection(db)
                    db.close()
                    last_anomaly_check = current_time
                except Exception as e:
                    logger.error(f"Error running anomaly detection: {str(e)}")

            asyncio.sleep(1)


background_manager = BackgroundTaskManager()
