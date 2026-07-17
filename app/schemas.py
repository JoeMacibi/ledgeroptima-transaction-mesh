from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models import TransactionStatus


class TransactionBase(BaseModel):
    transaction_id: str
    merchant_id: str
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    status: TransactionStatus = TransactionStatus.PENDING


class TransactionCreate(TransactionBase):
    latency_ms: float = Field(..., ge=0)
    processing_time_ms: float = Field(..., ge=0)
    error_message: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    latency_ms: float
    processing_time_ms: float
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class QueryPerformanceResponse(BaseModel):
    id: int
    query_hash: str
    query_text: str
    execution_time_ms: float
    rows_affected: int
    query_type: str
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AnomalyResponse(BaseModel):
    id: int
    anomaly_type: str
    severity: str
    merchant_id: Optional[str]
    metric_name: str
    baseline_value: float
    observed_value: float
    deviation_sigma: float
    description: str
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MerchantMetricsResponse(BaseModel):
    merchant_id: str
    merchant_name: str
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    total_volume: float
    avg_latency_ms: float
    last_activity: datetime

    class Config:
        from_attributes = True


class SystemHealthResponse(BaseModel):
    id: int
    total_transactions_hour: int
    successful_rate: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    db_connection_pool_active: int
    db_query_queue_length: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    total_transactions_today: int
    successful_rate: float
    avg_latency_ms: float
    active_merchants: int
    unresolved_anomalies: int
    p99_latency_ms: float
