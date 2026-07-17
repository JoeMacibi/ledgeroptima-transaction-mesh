from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models import Transaction, TransactionStatus, MerchantMetrics
from app.schemas import MerchantMetricsResponse

router = APIRouter(prefix="/api/merchants", tags=["merchants"])


@router.get("/", response_model=List[MerchantMetricsResponse])
def get_all_merchants(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    merchants = db.query(MerchantMetrics).order_by(
        desc(MerchantMetrics.last_activity)
    ).offset(offset).limit(limit).all()
    return merchants


@router.get("/{merchant_id}", response_model=MerchantMetricsResponse)
def get_merchant_details(merchant_id: str, db: Session = Depends(get_db)):
    merchant = db.query(MerchantMetrics).filter(
        MerchantMetrics.merchant_id == merchant_id
    ).first()
    
    if not merchant:
        return {
            "merchant_id": merchant_id,
            "merchant_name": merchant_id,
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "total_volume": 0.0,
            "avg_latency_ms": 0.0,
            "last_activity": datetime.utcnow(),
        }
    
    return merchant


@router.get("/{merchant_id}/trends")
def get_merchant_trends(
    merchant_id: str,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    cutoff_time = datetime.utcnow() - timedelta(days=days)
    
    trends = db.query(
        func.date(Transaction.created_at).label("day"),
        func.count(Transaction.id).label("count"),
        func.avg(Transaction.latency_ms).label("avg_latency"),
        func.sum(Transaction.amount).label("volume"),
    ).filter(
        and_(
            Transaction.merchant_id == merchant_id,
            Transaction.created_at >= cutoff_time,
        )
    ).group_by(func.date(Transaction.created_at)).all()
    
    return [
        {
            "day": str(trend.day),
            "transaction_count": trend.count,
            "avg_latency_ms": round(float(trend.avg_latency or 0), 2),
            "total_volume": round(float(trend.volume or 0), 2),
        }
        for trend in trends
    ]


@router.get("/{merchant_id}/performance")
def get_merchant_performance(
    merchant_id: str,
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    total = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.merchant_id == merchant_id,
            Transaction.created_at >= cutoff_time,
        )
    ).scalar() or 0
    
    successful = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.created_at >= cutoff_time,
        )
    ).scalar() or 0
    
    failed = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= cutoff_time,
        )
    ).scalar() or 0
    
    avg_latency = db.query(func.avg(Transaction.latency_ms)).filter(
        and_(
            Transaction.merchant_id == merchant_id,
            Transaction.created_at >= cutoff_time,
        )
    ).scalar() or 0.0
    
    total_volume = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.created_at >= cutoff_time,
        )
    ).scalar() or 0.0
    
    success_rate = (successful / total * 100) if total > 0 else 0.0
    
    return {
        "merchant_id": merchant_id,
        "total_transactions": total,
        "successful": successful,
        "failed": failed,
        "success_rate": round(success_rate, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "total_volume": round(total_volume, 2),
    }
