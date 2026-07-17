# LedgerOptima Telemetry Dashboard

Enterprise-grade transaction telemetry portal with real-time monitoring, merchant analytics, anomaly detection, and query performance tracking.

## Architecture

- **Backend**: FastAPI with PostgreSQL
- **Frontend**: Jinja2 templates + JavaScript/HTMX
- **Data Pipeline**: Synthetic transaction generation, anomaly detection engine
- **Deployment**: Docker Compose (PostgreSQL + FastAPI)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and setup**
```bash
cd ledgeroptima-telemetry-dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
```

3. **Initialize database**
```bash
python scripts/init_db.py
```

4. **Start the server**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Access dashboard**
Navigate to http://localhost:8000

### Docker Deployment

```bash
docker-compose up -d
```

The dashboard will be available at http://localhost:8000

## Features

### Real-time Transaction Monitoring
- Live transaction feed with status, latency, and merchant info
- 5-second auto-refresh with color-coded status indicators
- Transaction volume and success rate metrics

### Merchant Performance Analytics
- Per-merchant transaction statistics
- Success rates, volume trends, and latency tracking
- 7-day performance trends with daily aggregation

### Anomaly Detection & Alerts
- 3-sigma latency spike detection
- Error rate surge identification
- Per-merchant performance degradation alerts
- Automatic severity classification (Low/Medium/High/Critical)

### Query Performance Tracking
- Slow query identification (>50ms threshold)
- Query type classification (SELECT, INSERT, UPDATE, DELETE)
- Execution time trends and row count analysis
- Index optimization recommendations

### System Health Dashboard
- Hourly transaction throughput
- Success rate with health status
- Latency percentiles (P50, P95, P99)
- Real-time system status indicator

## API Endpoints

### Transactions
- `GET /api/transactions/recent` - Recent transactions (paginated)
- `GET /api/transactions/by-merchant/{merchant_id}` - Merchant transactions
- `GET /api/transactions/status/{status}` - Transactions by status
- `GET /api/transactions/stats` - Aggregate statistics

### Merchants
- `GET /api/merchants/` - All merchants with metrics
- `GET /api/merchants/{merchant_id}` - Merchant details
- `GET /api/merchants/{merchant_id}/trends` - 7-day trends
- `GET /api/merchants/{merchant_id}/performance` - Performance metrics

### System
- `GET /api/system/health` - System health metrics
- `GET /api/system/queries/slow` - Slow query log
- `GET /api/system/dashboard-summary` - Dashboard summary metrics

## Database Schema

### Tables
- `transactions` - Transaction records with status and latency
- `merchant_metrics` - Aggregated merchant statistics
- `query_performance` - Database query execution metrics
- `anomalies` - Detected anomalies and alerts
- `system_health` - Hourly system health snapshots

### Indexing Strategy
- Composite indexes on `(merchant_id, created_at)`
- Composite indexes on `(status, created_at)`
- Hash indexes on `transaction_id`
- Indexes on slow query thresholds

## Configuration

Environment variables in `.env`:

```
DEBUG=True
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/telemetry
TRANSACTION_BATCH_SIZE=100
ANOMALY_CHECK_INTERVAL=300
SYNTHETIC_DATA_RATE=100
```

## Anomaly Detection

The system runs anomaly detection every 5 minutes:

1. **Latency Anomalies**: Detects when latency deviates >3σ from baseline
2. **Error Rate Spikes**: Identifies sudden increases in failure rates
3. **Merchant Anomalies**: Flags individual merchants with >20% error rate

Severity levels: Low, Medium, High, Critical

## Performance Considerations

- Connection pooling: 20 base + 40 overflow connections
- Pagination on all list endpoints (max 1000 items)
- Indexes on hot query paths
- Background tasks for non-blocking data generation

## Development

### Running tests
```bash
pytest
```

### Code style
```bash
black app/
ruff check app/
mypy app/
```

## Production Deployment

For production deployments:

1. Set `DEBUG=False`
2. Use strong database credentials
3. Configure appropriate `SYNTHETIC_DATA_RATE` based on target TPS
4. Set up log aggregation (ELK, CloudWatch, etc.)
5. Configure monitoring and alerting
6. Enable database backups
7. Use environment-specific `.env` files

## License

Proprietary - LedgerOptima Enterprise Telemetry Platform
