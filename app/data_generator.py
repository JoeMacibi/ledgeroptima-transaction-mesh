import random
import uuid
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Transaction, TransactionStatus, MerchantMetrics, QueryPerformance

logger = logging.getLogger(__name__)

MERCHANTS = [
    "tech_startup_001",
    "retail_chain_002",
    "saas_platform_003",
    "ecommerce_store_004",
    "fintech_app_005",
    "subscription_service_006",
    "marketplace_007",
    "payment_processor_008",
    "digital_media_009",
    "logistics_provider_010",
]

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "INR"]


def _exponential_random(lambda_val: float) -> float:
    """Generate exponential random variable."""
    import math
    r = random.random()
    return -lambda_val * math.log(r)


def generate_transaction(db: Session) -> None:
    """Generate a single synthetic transaction."""
    merchant_id = random.choice(MERCHANTS)
    
    base_latency = _exponential_random(0.05) + 10
    latency_ms = max(5, base_latency + random.gauss(0, 5))
    
    processing_time_ms = latency_ms * random.uniform(0.7, 1.3)
    
    rand = random.random()
    if rand < 0.92:
        status = TransactionStatus.COMPLETED
    elif rand < 0.97:
        status = TransactionStatus.FAILED
    elif rand < 0.99:
        status = TransactionStatus.TIMEOUT
    else:
        status = TransactionStatus.PENDING
    
    amount = random.uniform(10, 5000)
    
    error_message = None
    if status == TransactionStatus.FAILED:
        error_message = random.choice([
            "Insufficient funds",
            "Card declined",
            "Gateway timeout",
            "Invalid merchant",
        ])
    elif status == TransactionStatus.TIMEOUT:
        error_message = "Request timeout after 30 seconds"
    
    transaction = Transaction(
        transaction_id=str(uuid.uuid4()),
        merchant_id=merchant_id,
        amount=amount,
        currency=random.choice(CURRENCIES),
        status=status,
        latency_ms=latency_ms,
        processing_time_ms=processing_time_ms,
        error_message=error_message,
        created_at=datetime.utcnow() - timedelta(seconds=random.randint(0, 3600)),
        completed_at=datetime.utcnow() if status != TransactionStatus.PENDING else None,
    )
    
    db.add(transaction)
    
    merchant = db.query(MerchantMetrics).filter(
        MerchantMetrics.merchant_id == merchant_id
    ).first()
    
    if not merchant:
        merchant = MerchantMetrics(
            merchant_id=merchant_id,
            merchant_name=f"{merchant_id.replace('_', ' ').title()}",
            total_transactions=0,
            successful_transactions=0,
            failed_transactions=0,
            total_volume=0.0,
            avg_latency_ms=0.0,
        )
        db.add(merchant)
    
    merchant.total_transactions += 1
    if status == TransactionStatus.COMPLETED:
        merchant.successful_transactions += 1
        merchant.total_volume += amount
    elif status == TransactionStatus.FAILED:
        merchant.failed_transactions += 1
    
    merchant.avg_latency_ms = (
        (merchant.avg_latency_ms * (merchant.total_transactions - 1) + latency_ms) 
        / merchant.total_transactions
    )
    merchant.last_activity = datetime.utcnow()


def generate_query_performance(db: Session) -> None:
    """Generate a synthetic query performance record."""
    query_types = ["SELECT", "UPDATE", "INSERT", "DELETE"]
    query_type = random.choice(query_types)
    
    if query_type == "SELECT":
        base_time = _exponential_random(0.1) + 5
    else:
        base_time = _exponential_random(0.2) + 2
    
    execution_time_ms = max(0.5, base_time + random.gauss(0, 2))
    
    slow_threshold = 100 if query_type == "SELECT" else 50
    if random.random() < 0.05:
        execution_time_ms = random.uniform(slow_threshold, slow_threshold * 3)
    
    query_text = f"{query_type} query on telemetry tables"
    query_hash = str(uuid.uuid4())[:16]
    
    rows_affected = random.randint(1, 10000) if query_type != "SELECT" else random.randint(100, 100000)
    
    query_perf = QueryPerformance(
        query_hash=query_hash,
        query_text=query_text,
        execution_time_ms=execution_time_ms,
        rows_affected=rows_affected,
        query_type=query_type,
        success=random.random() > 0.02,
        created_at=datetime.utcnow() - timedelta(seconds=random.randint(0, 3600)),
    )
    
    db.add(query_perf)


def generate_batch(db: Session, batch_size: int = 100) -> None:
    """Generate a batch of synthetic transactions and queries."""
    try:
        for _ in range(batch_size):
            generate_transaction(db)
        
        for _ in range(batch_size // 5):
            generate_query_performance(db)
        
        db.commit()
        logger.info(f"Generated {batch_size} transactions and {batch_size // 5} query records")
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating batch: {str(e)}")


def seed_initial_data(db: Session, num_transactions: int = 5000) -> None:
    """Seed the database with initial synthetic data."""
    try:
        existing = db.query(Transaction).count()
        if existing > 0:
            logger.info(f"Database already has {existing} transactions, skipping seed")
            return
        
        logger.info(f"Seeding database with {num_transactions} initial transactions...")
        
        batch_size = 500
        for i in range(0, num_transactions, batch_size):
            current_batch_size = min(batch_size, num_transactions - i)
            for _ in range(current_batch_size):
                generate_transaction(db)
            
            if (i + batch_size) % 2000 == 0:
                db.commit()
                logger.info(f"Seeded {i + batch_size} transactions...")
        
        db.commit()
        logger.info(f"Seeding complete: {num_transactions} transactions added")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding initial data: {str(e)}")
