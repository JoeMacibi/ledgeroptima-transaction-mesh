from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Enum, Index, ForeignKey,
    UniqueConstraint, CheckConstraint, Text, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(64), unique=True, nullable=False, index=True)
    merchant_id = Column(String(64), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    
    latency_ms = Column(Float, nullable=False)
    processing_time_ms = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    error_message = Column(Text, nullable=True)
    
    __table_args__ = (
        Index("idx_merchant_created", "merchant_id", "created_at"),
        Index("idx_status_created", "status", "created_at"),
        CheckConstraint("amount > 0"),
        CheckConstraint("latency_ms >= 0"),
        CheckConstraint("processing_time_ms >= 0"),
    )


class QueryPerformance(Base):
    __tablename__ = "query_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(64), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    
    execution_time_ms = Column(Float, nullable=False)
    rows_affected = Column(Integer, default=0)
    
    query_type = Column(String(32), nullable=False)
    success = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index("idx_query_created", "query_hash", "created_at"),
        Index("idx_slow_queries", "execution_time_ms", "created_at"),
    )


class AnomalyDetection(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    anomaly_type = Column(String(64), nullable=False, index=True)
    severity = Column(String(16), nullable=False)
    
    merchant_id = Column(String(64), nullable=True, index=True)
    metric_name = Column(String(128), nullable=False)
    
    baseline_value = Column(Float, nullable=False)
    observed_value = Column(Float, nullable=False)
    deviation_sigma = Column(Float, nullable=False)
    
    description = Column(Text, nullable=False)
    resolved = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("idx_anomaly_created", "anomaly_type", "created_at"),
        Index("idx_unresolved", "resolved", "created_at"),
    )


class MerchantMetrics(Base):
    __tablename__ = "merchant_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(64), unique=True, nullable=False, index=True)
    merchant_name = Column(String(255), nullable=False)
    
    total_transactions = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    
    total_volume = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_merchant_last_activity", "last_activity"),
    )


class SystemHealth(Base):
    __tablename__ = "system_health"
    
    id = Column(Integer, primary_key=True, index=True)
    
    total_transactions_hour = Column(Integer, default=0)
    successful_rate = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    p50_latency_ms = Column(Float, default=0.0)
    p95_latency_ms = Column(Float, default=0.0)
    p99_latency_ms = Column(Float, default=0.0)
    
    db_connection_pool_active = Column(Integer, default=0)
    db_query_queue_length = Column(Integer, default=0)
    
    status = Column(String(32), default="healthy")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index("idx_health_created", "created_at"),
    )
