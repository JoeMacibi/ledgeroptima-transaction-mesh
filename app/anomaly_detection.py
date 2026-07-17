import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import Transaction, AnomalyDetection, TransactionStatus

logger = logging.getLogger(__name__)


def detect_latency_anomalies(db: Session) -> None:
    """Detect anomalies in transaction latency using statistical methods."""
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    day_ago = datetime.utcnow() - timedelta(days=1)
    
    recent_latencies = db.query(Transaction.latency_ms).filter(
        Transaction.created_at >= hour_ago
    ).all()
    
    if not recent_latencies or len(recent_latencies) < 10:
        return
    
    recent_values = [l[0] for l in recent_latencies]
    baseline_latencies = db.query(Transaction.latency_ms).filter(
        and_(
            Transaction.created_at >= day_ago,
            Transaction.created_at < hour_ago,
        )
    ).all()
    
    if baseline_latencies and len(baseline_latencies) >= 10:
        baseline_values = [l[0] for l in baseline_latencies]
        baseline_mean = sum(baseline_values) / len(baseline_values)
        
        variance = sum((x - baseline_mean) ** 2 for x in baseline_values) / len(baseline_values)
        baseline_std = variance ** 0.5
        
        current_mean = np.mean(recent_values)
        
        if baseline_std > 0:
            deviation_sigma = abs(current_mean - baseline_mean) / baseline_std
            
            if deviation_sigma > 3:
                existing = db.query(AnomalyDetection).filter(
                    and_(
                        AnomalyDetection.anomaly_type == "latency_spike",
                        AnomalyDetection.resolved == False,
                    )
                ).first()
                
                if not existing:
                    anomaly = AnomalyDetection(
                        anomaly_type="latency_spike",
                        severity="high" if deviation_sigma > 4 else "medium",
                        merchant_id=None,
                        metric_name="transaction_latency_ms",
                        baseline_value=float(baseline_mean),
                        observed_value=float(current_mean),
                        deviation_sigma=float(deviation_sigma),
                        description=f"Transaction latency increased from {baseline_mean:.2f}ms to {current_mean:.2f}ms ({deviation_sigma:.2f}σ deviation)",
                    )
                    db.add(anomaly)
                    db.commit()
                    logger.info(f"Detected latency anomaly: {deviation_sigma:.2f}σ")


def detect_error_rate_anomalies(db: Session) -> None:
    """Detect anomalies in error rates."""
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    day_ago = datetime.utcnow() - timedelta(days=1)
    
    total_hour = db.query(func.count(Transaction.id)).filter(
        Transaction.created_at >= hour_ago
    ).scalar() or 0
    
    failed_hour = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= hour_ago,
        )
    ).scalar() or 0
    
    if total_hour < 10:
        return
    
    current_error_rate = (failed_hour / total_hour) * 100 if total_hour > 0 else 0
    
    total_day = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.created_at >= day_ago,
            Transaction.created_at < hour_ago,
        )
    ).scalar() or 0
    
    failed_day = db.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= day_ago,
            Transaction.created_at < hour_ago,
        )
    ).scalar() or 0
    
    baseline_error_rate = (failed_day / total_day) * 100 if total_day > 0 else 0
    
    if baseline_error_rate > 0:
        error_increase_pct = ((current_error_rate - baseline_error_rate) / baseline_error_rate) * 100
        
        if error_increase_pct > 50 and current_error_rate > 5:
            existing = db.query(AnomalyDetection).filter(
                and_(
                    AnomalyDetection.anomaly_type == "error_rate_spike",
                    AnomalyDetection.resolved == False,
                )
            ).first()
            
            if not existing:
                anomaly = AnomalyDetection(
                    anomaly_type="error_rate_spike",
                    severity="critical" if current_error_rate > 10 else "high",
                    merchant_id=None,
                    metric_name="error_rate_percent",
                    baseline_value=baseline_error_rate,
                    observed_value=current_error_rate,
                    deviation_sigma=error_increase_pct / 100,
                    description=f"Error rate increased from {baseline_error_rate:.2f}% to {current_error_rate:.2f}% ({error_increase_pct:.1f}% increase)",
                )
                db.add(anomaly)
                db.commit()
                logger.info(f"Detected error rate anomaly: {current_error_rate:.2f}%")


def detect_merchant_anomalies(db: Session) -> None:
    """Detect anomalies in individual merchant performance."""
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    day_ago = datetime.utcnow() - timedelta(days=1)
    
    merchants = db.query(func.distinct(Transaction.merchant_id)).filter(
        Transaction.created_at >= hour_ago
    ).all()
    
    for (merchant_id,) in merchants:
        total_hour = db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.merchant_id == merchant_id,
                Transaction.created_at >= hour_ago,
            )
        ).scalar() or 0
        
        if total_hour < 5:
            continue
        
        failed_hour = db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.merchant_id == merchant_id,
                Transaction.status == TransactionStatus.FAILED,
                Transaction.created_at >= hour_ago,
            )
        ).scalar() or 0
        
        merchant_error_rate = (failed_hour / total_hour) * 100 if total_hour > 0 else 0
        
        if merchant_error_rate > 20:
            existing = db.query(AnomalyDetection).filter(
                and_(
                    AnomalyDetection.anomaly_type == "merchant_error_surge",
                    AnomalyDetection.merchant_id == merchant_id,
                    AnomalyDetection.resolved == False,
                )
            ).first()
            
            if not existing:
                anomaly = AnomalyDetection(
                    anomaly_type="merchant_error_surge",
                    severity="high",
                    merchant_id=merchant_id,
                    metric_name="merchant_error_rate",
                    baseline_value=0.0,
                    observed_value=merchant_error_rate,
                    deviation_sigma=merchant_error_rate / 10,
                    description=f"Merchant {merchant_id} experiencing high error rate: {merchant_error_rate:.2f}%",
                )
                db.add(anomaly)
                db.commit()
                logger.info(f"Detected merchant anomaly for {merchant_id}: {merchant_error_rate:.2f}% errors")


def run_anomaly_detection(db: Session) -> None:
    """Run all anomaly detection checks."""
    try:
        detect_latency_anomalies(db)
        detect_error_rate_anomalies(db)
        detect_merchant_anomalies(db)
        logger.info("Anomaly detection cycle completed")
    except Exception as e:
        logger.error(f"Error during anomaly detection: {str(e)}")
