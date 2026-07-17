from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models import Transaction, TransactionStatus, MerchantMetrics
from app.schemas import TransactionResponse, TransactionCreate

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(
        transaction_id=transaction.transaction_id,
        merchant_id=transaction.merchant_id,
        amount=transaction.amount,
        currency=transaction.currency,
        status=transaction.status,
        latency_ms=transaction.latency_ms,
        processing_time_ms=transaction.processing_time_ms,
        error_message=transaction.error_message,
        completed_at=datetime.utcnow() if transaction.status != TransactionStatus.PENDING else None,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/recent", response_model=List[TransactionResponse])
def get_recent_transactions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    transactions = db.query(Transaction).order_by(
        desc(Transaction.created_at)
    ).offset(offset).limit(limit).all()
    return transactions


@router.get("/by-merchant/{merchant_id}", response_model=List[TransactionResponse])
def get_merchant_transactions(
    merchant_id: str,
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    transactions = db.query(Transaction).filter(
        and_(
            Transaction.merchant_id == merchant_id,
            Transaction.created_at >= cutoff_time,
        )
    ).order_by(desc(Transaction.created_at)).limit(limit).all()
    return transactions


@router.get("/status/{status}")
def get_transactions_by_status(
    status: TransactionStatus,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    hours = 24
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    transactions = db.query(Transaction).filter(
        and_(
            Transaction.status == status,
            Transaction.created_at >= cutoff_time,
        )
    ).order_by(desc(Transaction.created_at)).limit(limit).all()
    return transactions


@router.get("/stats")
def get_transaction_stats(db: Session = Depends(get_db)):
    hours = 24
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    total = db.query(func.count(Transaction.id)).filter(
        Transaction.created_at >= cutoff_time
    ).scalar() or 0
    
    successful = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.created_at >= cutoff_time,
        )
    ).scalar() or 0
    
    failed = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= cutoff_time,
        )
    ).scalar() or 0
    
    avg_latency = db.query(func.avg(Transaction.latency_ms)).filter(
        Transaction.created_at >= cutoff_time
    ).scalar() or 0.0
    
    total_volume = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.created_at >= cutoff_time,
        )
    ).scalar() or 0.0
    
    success_rate = (successful / total * 100) if total > 0 else 0.0
    
    return {
        "total_transactions": total,
        "successful": successful,
        "failed": failed,
        "success_rate": round(success_rate, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "total_volume": round(total_volume, 2),
    }
