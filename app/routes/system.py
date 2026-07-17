from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import numpy as np

from app.database import get_db
from app.models import Transaction, SystemHealth, QueryPerformance, TransactionStatus
from app.schemas import SystemHealthResponse

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health", response_model=SystemHealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    total_hour = db.query(func.count(Transaction.id)).filter(
        Transaction.created_at >= hour_ago
    ).scalar() or 0
    
    successful_hour = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.created_at >= hour_ago,
        )
    ).scalar() or 0
    
    success_rate = (successful_hour / total_hour * 100) if total_hour > 0 else 0.0
    
    avg_latency = db.query(func.avg(Transaction.latency_ms)).filter(
        Transaction.created_at >= hour_ago
    ).scalar() or 0.0
    
    latencies = db.query(Transaction.latency_ms).filter(
        Transaction.created_at >= hour_ago
    ).all()
    
    if latencies:
        sorted_latencies = sorted([l[0] for l in latencies])
        p50 = sorted_latencies[int(len(sorted_latencies) * 0.50)]
        p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)]
    else:
        p50, p95, p99 = 0.0, 0.0, 0.0
    
    status = "healthy"
    if success_rate < 95:
        status = "degraded"
    if success_rate < 85:
        status = "critical"
    
    health = SystemHealth(
        total_transactions_hour=total_hour,
        successful_rate=round(success_rate, 2),
        avg_latency_ms=round(avg_latency, 2),
        p50_latency_ms=round(p50, 2),
        p95_latency_ms=round(p95, 2),
        p99_latency_ms=round(p99, 2),
        db_connection_pool_active=0,
        db_query_queue_length=0,
        status=status,
    )
    
    return health


@router.get("/queries/slow")
def get_slow_queries(
    threshold_ms: float = 100.0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    slow_queries = db.query(QueryPerformance).filter(
        and_(
            QueryPerformance.execution_time_ms >= threshold_ms,
            QueryPerformance.created_at >= hour_ago,
        )
    ).order_by(desc(QueryPerformance.execution_time_ms)).limit(limit).all()
    
    return [
        {
            "query_hash": q.query_hash,
            "query_type": q.query_type,
            "execution_time_ms": round(q.execution_time_ms, 2),
            "rows_affected": q.rows_affected,
            "created_at": q.created_at.isoformat(),
        }
        for q in slow_queries
    ]


@router.get("/dashboard-summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_today = db.query(func.count(Transaction.id)).filter(
        Transaction.created_at >= today_start
    ).scalar() or 0
    
    successful_today = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.created_at >= today_start,
        )
    ).scalar() or 0
    
    success_rate = (successful_today / total_today * 100) if total_today > 0 else 0.0
    
    avg_latency = db.query(func.avg(Transaction.latency_ms)).filter(
        Transaction.created_at >= today_start
    ).scalar() or 0.0
    
    active_merchants = db.query(func.count(func.distinct(Transaction.merchant_id))).filter(
        Transaction.created_at >= today_start
    ).scalar() or 0
    
    from app.models import AnomalyDetection
    unresolved_anomalies = db.query(func.count(AnomalyDetection.id)).filter(
        AnomalyDetection.resolved == False
    ).scalar() or 0
    
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    latencies = db.query(Transaction.latency_ms).filter(
        Transaction.created_at >= hour_ago
    ).all()
    
    p99 = 0.0
    if latencies:
        sorted_latencies = sorted([l[0] for l in latencies])
        p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)]
    
    return {
        "total_transactions_today": total_today,
        "successful_rate": round(success_rate, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "active_merchants": active_merchants,
        "unresolved_anomalies": unresolved_anomalies,
        "p99_latency_ms": round(p99, 2),
    }
