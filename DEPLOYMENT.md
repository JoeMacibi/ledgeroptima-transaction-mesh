# LedgerOptima Telemetry Dashboard - Deployment Guide

## Project Structure

```
ledgeroptima-telemetry-dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database session and initialization
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── data_generator.py    # Synthetic transaction generation
│   ├── anomaly_detection.py # Anomaly detection engine
│   ├── background_tasks.py  # Background task management
│   └── routes/
│       ├── __init__.py
│       ├── transactions.py  # Transaction endpoints
│       ├── merchants.py     # Merchant analytics endpoints
│       └── system.py        # System health endpoints
├── templates/
│   └── index.html           # Dashboard HTML template
├── static/
│   ├── css/
│   │   └── style.css        # Dashboard styling
│   └── js/
│       └── dashboard.js     # Dashboard JavaScript logic
├── scripts/
│   └── init_db.py           # Database initialization script
├── migrations/              # Alembic migration files
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project metadata
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # Project documentation
```

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- 4GB RAM minimum, 2+ CPU cores recommended

### Local Setup

1. **Clone repository**
```bash
git clone <repo-url>
cd ledgeroptima-telemetry-dashboard
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env .env.local
# Edit .env.local with your database credentials
```

5. **Initialize database**
```bash
python scripts/init_db.py
```

6. **Start development server**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

7. **Access dashboard**
Navigate to `http://localhost:8000`

## Docker Deployment

### Quick Start

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database on localhost:5432
- FastAPI server on localhost:8000
- Automatic database initialization
- Real-time data generation

### View Logs

```bash
docker-compose logs -f api
```

### Stop Services

```bash
docker-compose down
```

## Production Deployment

### Environment Configuration

Create `.env.production`:
```
DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=postgresql+psycopg://user:password@prod-db.example.com:5432/telemetry
SYNTHETIC_DATA_RATE=100
ANOMALY_CHECK_INTERVAL=300
```

### Database Setup

1. Create PostgreSQL database on production server
2. Run migrations
3. Set up automated backups

### Application Deployment

#### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app --timeout 120
```

#### Using systemd

Create `/etc/systemd/system/telemetry-dashboard.service`:

```ini
[Unit]
Description=LedgerOptima Telemetry Dashboard
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/telemetry-dashboard
Environment="PATH=/opt/telemetry-dashboard/venv/bin"
ExecStart=/opt/telemetry-dashboard/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app.main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable telemetry-dashboard
sudo systemctl start telemetry-dashboard
```

#### Using Docker on Production

```bash
docker build -t ledgeroptima:latest .
docker run -d \
  --name telemetry-api \
  --env-file .env.production \
  -p 8000:8000 \
  -v /var/log/telemetry:/app/logs \
  ledgeroptima:latest
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/telemetry`:

```nginx
upstream telemetry_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name telemetry.example.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://telemetry_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /opt/telemetry-dashboard/static/;
        expires 1h;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/telemetry /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring & Logging

### Application Logs

Monitor real-time logs:
```bash
tail -f /opt/telemetry-dashboard/logs/app.log
```

### Database Monitoring

Check connection pool usage:
```sql
SELECT 
    usename, 
    application_name, 
    state,
    COUNT(*) as connections
FROM pg_stat_activity
GROUP BY usename, application_name, state;
```

### Disk Space

Monitor database growth:
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Backup & Recovery

### PostgreSQL Backup

Daily backup:
```bash
pg_dump -h localhost -U postgres telemetry | gzip > /backups/telemetry-$(date +%Y%m%d).sql.gz
```

### Restore from Backup

```bash
gunzip < /backups/telemetry-20250101.sql.gz | psql -U postgres telemetry
```

## Performance Tuning

### Database Optimization

```sql
ANALYZE;
REINDEX DATABASE telemetry;
VACUUM ANALYZE;
```

### Connection Pool Tuning

Adjust in `app/config.py`:
```python
pool_size=20          # Base connections
max_overflow=40       # Extra connections under load
pool_pre_ping=True    # Validate connections
```

### Query Performance

Enable slow query logging in PostgreSQL:
```sql
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
```

## Troubleshooting

### Database Connection Errors

Check PostgreSQL is running:
```bash
pg_isready -h localhost -p 5432
```

### High CPU Usage

1. Check slow queries
2. Verify indexes exist
3. Adjust `SYNTHETIC_DATA_RATE`

### Memory Issues

1. Reduce `pool_size` and `max_overflow`
2. Lower `SYNTHETIC_DATA_RATE`
3. Increase server RAM

### Dashboard Not Loading

1. Check API health: `curl http://localhost:8000/health`
2. Verify database connection
3. Check browser console for JavaScript errors
4. Review application logs

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong database passwords
- [ ] Enable PostgreSQL SSL connections
- [ ] Configure firewall to restrict database access
- [ ] Set up HTTPS with valid certificates
- [ ] Enable authentication if multi-user access needed
- [ ] Rotate database credentials regularly
- [ ] Monitor for unauthorized access attempts
- [ ] Keep dependencies updated
- [ ] Configure log retention policies

## Scaling Considerations

### Horizontal Scaling

For multiple application instances:

1. Use load balancer (Nginx, HAProxy)
2. Shared PostgreSQL database
3. Redis for background task coordination

### Vertical Scaling

- Increase server CPU and RAM
- Tune connection pool settings
- Optimize database queries

### Data Retention

Consider archiving old data:
```sql
DELETE FROM transactions 
WHERE created_at < NOW() - INTERVAL '90 days';
```

## Support & Maintenance

- Review logs weekly for errors
- Check disk usage monthly
- Update dependencies quarterly
- Test backup recovery procedures
- Monitor database growth trends
