# Quick Start Guide - 5 Minutes to Running Dashboard

## Option 1: Docker Compose (Recommended - Fastest)

### Requirements
- Docker Desktop installed
- 4GB disk space available

### Steps

```bash
# 1. Navigate to project directory
cd ledgeroptima-telemetry-dashboard

# 2. Start all services
docker-compose up -d

# 3. Wait for database to initialize (5-10 seconds)
sleep 10

# 4. Open dashboard
open http://localhost:8000
# or paste in browser: http://localhost:8000
```

### That's it! 🎉

The dashboard is now running with:
- PostgreSQL database: localhost:5432
- FastAPI server: localhost:8000  
- Auto-generated sample data
- Live anomaly detection

### Stopping Services
```bash
docker-compose down
```

### Viewing Logs
```bash
docker-compose logs -f api
```

---

## Option 2: Local Python (Manual)

### Requirements
- Python 3.11+
- PostgreSQL 15+ installed locally
- 2GB disk space

### Steps

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python scripts/init_db.py

# 4. Start development server
python -m uvicorn app.main:app --reload --port 8000

# 5. Open dashboard
# Navigate to: http://localhost:8000
```

---

## What You'll See

### Dashboard Overview
- **Summary Cards**: Transaction volume, success rate, latency, active merchants
- **Real-time Transactions**: Live feed of transactions with status
- **Merchant Analytics**: Performance metrics for each merchant
- **Anomalies**: Detected issues and alerts
- **Query Performance**: Slow database queries
- **System Health**: Overall system status and metrics

### Navigation
- Click tabs at the top to switch between views
- Refresh buttons update data on demand
- Dashboard auto-refreshes every 10-30 seconds

### Sample Data
The system starts with:
- 5,000 initial transactions
- 10 test merchants
- Continuous data generation (100 tx/sec)
- Automatic anomaly detection

---

## API Examples

### Get Recent Transactions
```bash
curl http://localhost:8000/api/transactions/recent?limit=10
```

### Get System Health
```bash
curl http://localhost:8000/api/system/health
```

### Get Merchant Performance
```bash
curl http://localhost:8000/api/merchants/tech_startup_001/performance
```

### View All Merchants
```bash
curl http://localhost:8000/api/merchants/
```

---

## Common Tasks

### View Dashboard
- Open browser to http://localhost:8000

### Check API Health
```bash
curl http://localhost:8000/health
```

### Reset Database (Docker)
```bash
docker-compose down -v
docker-compose up -d
```

### Reset Database (Local)
```bash
python scripts/init_db.py
```

### Stop Services (Docker)
```bash
docker-compose down
```

### Stop Services (Local)
```bash
# Press Ctrl+C in terminal
```

---

## Troubleshooting

### "Connection refused" on localhost:8000
- Wait 10 seconds for database to initialize
- Check if port 8000 is already in use
- Try: `lsof -i :8000` (Mac/Linux)

### "Database connection error"
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify credentials are correct

### "Docker service won't start"
- Check Docker is installed: `docker --version`
- Check Docker daemon is running
- Try: `docker-compose up -d --force-recreate`

### Dashboard shows no data
- Wait 30 seconds for data generation
- Refresh browser (Cmd+R or Ctrl+R)
- Check browser console for errors (F12)

### High CPU/Memory usage
- This is normal during initial data generation
- Will stabilize after 2-3 minutes
- Data generation rate set to 100 tx/sec (configurable)

---

## Configuration

### Change Data Generation Rate
Edit `.env`:
```
SYNTHETIC_DATA_RATE=100  # transactions per second (default)
SYNTHETIC_DATA_RATE=50   # slower
SYNTHETIC_DATA_RATE=500  # faster
```

Then restart services.

### Change Anomaly Detection Interval
Edit `.env`:
```
ANOMALY_CHECK_INTERVAL=300  # seconds (default = 5 minutes)
ANOMALY_CHECK_INTERVAL=60   # every 1 minute
```

---

## Next Steps

### Learn More
- Read `README.md` for full feature documentation
- Read `PROJECT_SUMMARY.md` for technical details
- Read `DEPLOYMENT.md` for production setup

### Customize Dashboard
- Edit `templates/index.html` for layout
- Edit `static/css/style.css` for styling
- Edit `static/js/dashboard.js` for behavior

### Add Features
- Create new endpoints in `app/routes/`
- Add new database models in `app/models.py`
- Extend anomaly detection in `app/anomaly_detection.py`

### Deploy to Production
- See `DEPLOYMENT.md` for Nginx, Systemd, and Docker production setup
- Configure environment variables in `.env.production`
- Set `DEBUG=False` before production

---

## Performance Expectations

| Metric | Value |
|--------|-------|
| Dashboard load time | <2 seconds |
| API response time | <50ms avg |
| Transaction ingestion | 100 tx/sec |
| Anomaly detection | 5-minute cycles |
| Browser auto-refresh | 10-30 seconds |

---

## Support

- Dashboard: http://localhost:8000
- API docs: http://localhost:8000/docs (when running locally)
- Logs: `docker-compose logs -f api`
- Issues: Check DEPLOYMENT.md troubleshooting section

---

## Success Checklist

- [ ] Services started successfully
- [ ] Dashboard loads in browser
- [ ] Transactions visible in "Real-time" tab
- [ ] Merchants showing in "Analytics" tab
- [ ] System health metrics displaying
- [ ] Anomalies detecting correctly
- [ ] Query performance tracking

If all checkmarks complete, you're ready to explore!

---

**Time to deployment: ~5 minutes** ⚡

Start with Docker Compose, then explore the code. Production deployment guides available in DEPLOYMENT.md.
