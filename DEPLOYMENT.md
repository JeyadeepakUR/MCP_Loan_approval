# Production Deployment Guide

## 🚀 Deployment Options

### Option 1: Cloud Platform (Recommended)

#### **Render.com (Free Tier Available)**
1. Create account at https://render.com
2. Create new "Web Service"
3. Connect your GitHub repo (or upload code)
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
5. Add to `requirements.txt`:
   ```
   gunicorn>=21.0.0
   ```
6. Deploy! You'll get a URL like: `https://your-app.onrender.com`

**Cost**: Free tier available (sleeps after 15 min inactivity)

---

#### **Railway.app**
1. Create account at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo
4. Railway auto-detects Python and deploys
5. You get: `https://your-app.railway.app`

**Cost**: $5/month (500 hours free trial)

---

#### **Heroku**
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

**Cost**: $7/month (Eco dyno)

---

### Option 2: VPS (Full Control)

#### **DigitalOcean / AWS / Azure**
1. Create Ubuntu server ($5-10/month)
2. SSH into server
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip nginx
   ```
4. Clone your code:
   ```bash
   git clone your-repo
   cd loan_origination_system
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
5. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
6. Configure Nginx as reverse proxy
7. Add SSL with Let's Encrypt

**Cost**: $5-10/month

---

### Option 3: Docker (Any Platform)

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

2. Build and run:
   ```bash
   docker build -t loan-app .
   docker run -p 5000:5000 loan-app
   ```

3. Deploy to any Docker hosting (AWS ECS, Google Cloud Run, etc.)

---

## 📊 Handling New Users (Beyond Mock Data)

### Problem
Currently using **mock CRM data** (10 hardcoded users). Real production needs:
- ✅ New user registration
- ✅ Real KYC verification
- ✅ Actual credit bureau integration

### Solution Options

#### **Option A: Database Integration (Recommended)**

Add SQLite/PostgreSQL for user storage:

1. Install dependencies:
   ```bash
   pip install sqlalchemy psycopg2-binary
   ```

2. Create `services/database.py`:
   ```python
   from sqlalchemy import create_engine, Column, String, Integer, Float
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import sessionmaker
   
   Base = declarative_base()
   
   class Customer(Base):
       __tablename__ = 'customers'
       
       customer_id = Column(String, primary_key=True)
       name = Column(String)
       pan = Column(String, unique=True)
       employment_type = Column(String)
       monthly_income = Column(Float)
       phone = Column(String)
       email = Column(String)
   
   # For production: PostgreSQL
   engine = create_engine('postgresql://user:pass@host/dbname')
   
   # For development: SQLite
   engine = create_engine('sqlite:///customers.db')
   
   Base.metadata.create_all(engine)
   Session = sessionmaker(bind=engine)
   ```

3. Modify `verification_agent.py` to check database first, then mock data

**Benefits**:
- ✅ Store unlimited users
- ✅ Real-time registration
- ✅ Production-ready

---

#### **Option B: External API Integration**

Connect to real services:

1. **KYC Verification**: Use APIs like:
   - Aadhaar verification (India)
   - Jumio, Onfido (Global)
   - Stripe Identity

2. **Credit Bureau**: Integrate with:
   - CIBIL, Experian (India)
   - Equifax, TransUnion (Global)

Example:
```python
import requests

def verify_pan_real(pan):
    response = requests.post(
        'https://api.kyc-provider.com/verify',
        json={'pan': pan},
        headers={'Authorization': 'Bearer YOUR_API_KEY'}
    )
    return response.json()
```

**Benefits**:
- ✅ Real verification
- ✅ Accurate credit scores
- ✅ Compliance-ready

**Cost**: $0.10-$1 per verification

---

#### **Option C: Hybrid Approach (Best for Demo → Production)**

1. **Development**: Use mock data
2. **Staging**: Use database with test data
3. **Production**: Use external APIs

Configure via environment variables:
```python
import os

if os.getenv('ENV') == 'production':
    # Use real APIs
    from services.real_kyc import verify_customer
else:
    # Use mock data
    from services.mock_data import MockCRMService
```

---

## 🔒 Production Checklist

Before deploying:

### Security
- [ ] Change `SECRET_KEY` in `app.py`
- [ ] Set `debug=False` in production
- [ ] Add HTTPS (SSL certificate)
- [ ] Enable CORS properly
- [ ] Add rate limiting
- [ ] Sanitize user inputs

### Database
- [ ] Use PostgreSQL (not SQLite) for production
- [ ] Set up database backups
- [ ] Add connection pooling
- [ ] Use environment variables for credentials

### Monitoring
- [ ] Add logging (Sentry, LogRocket)
- [ ] Set up health checks
- [ ] Monitor API response times
- [ ] Track error rates

### Scalability
- [ ] Use Redis for session storage (not in-memory)
- [ ] Add caching for static data
- [ ] Configure auto-scaling
- [ ] Set up load balancer

---

## 🎯 Recommended Deployment Path

### For Demo/POC:
```
1. Deploy to Render.com (free)
2. Use mock data (current setup)
3. Share URL with stakeholders
```

### For Production:
```
1. Set up PostgreSQL database
2. Integrate real KYC/credit APIs
3. Deploy to Railway/Heroku ($5-10/month)
4. Add monitoring (Sentry)
5. Configure custom domain
6. Add SSL certificate
```

---

## 💡 Quick Deploy (5 Minutes)

**Render.com (Easiest)**:
1. Push code to GitHub
2. Go to https://render.com
3. Click "New" → "Web Service"
4. Connect GitHub repo
5. Set start command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
6. Click "Create Web Service"
7. Done! You get a live URL

**No LLM hosting needed** - the system uses rule-based matching (fast & accurate)!

---

## ❓ FAQ

**Q: Do I need to host Ollama/LLM?**
A: **No!** The system uses rule-based matching (currently disabled Ollama). It's faster and works perfectly for structured loan conversations.

**Q: What about new users not in mock data?**
A: Options:
1. Add to `services/mock_data.py` manually (quick fix)
2. Add database (see Option A above)
3. Integrate real KYC API (production)

**Q: How much does deployment cost?**
A: 
- Free: Render.com (with limitations)
- $5/month: Railway, DigitalOcean
- $7/month: Heroku

**Q: Can I use SQLite in production?**
A: Not recommended. Use PostgreSQL for production (better concurrency, backups, scalability).

**Q: How do I add SSL/HTTPS?**
A: Most platforms (Render, Railway, Heroku) provide free SSL automatically!

---

## 🚀 Next Steps

1. **Choose deployment platform** (Render.com recommended for start)
2. **Push code to GitHub** (if not already)
3. **Deploy** (follow platform instructions above)
4. **Test** with the provided test users
5. **Add database** when ready for real users
6. **Integrate APIs** for production KYC/credit checks

**The system is ready to deploy as-is!** 🎉
