# Render.com Deployment Guide

## 🚀 One-Click Deployment

Your repository is now configured for **automatic deployment** on Render.com!

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Go to Render.com**
   - Visit: https://render.com
   - Sign up/login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select repository: `JeyadeepakUR/MCP_Loan_approval`

3. **Render Auto-Detects Configuration**
   - Render will find `render.yaml` automatically
   - All settings pre-configured!
   - Just click **"Create Web Service"**

4. **Done!**
   - Render builds and deploys automatically
   - You'll get a URL: `https://bfsi-loan-system.onrender.com`
   - Auto-deploys on every push to `main` branch

---

### Option 2: Deploy via Blueprint (Even Easier!)

1. **Click this button** (add to your GitHub README):
   ```markdown
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/JeyadeepakUR/MCP_Loan_approval)
   ```

2. **One-click deploy** - Render sets everything up automatically!

---

## 📋 What's Configured

### `render.yaml` Settings:
- ✅ **Service Type**: Web Service
- ✅ **Environment**: Python 3.11
- ✅ **Region**: Oregon (free tier)
- ✅ **Plan**: Free
- ✅ **Build Command**: `pip install -r requirements.txt`
- ✅ **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
- ✅ **Health Check**: `/health` endpoint
- ✅ **Auto Deploy**: Enabled (deploys on git push)

### Free Tier Limits:
- ✅ 750 hours/month (enough for 24/7)
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ 512 MB RAM
- ✅ Custom domain support
- ✅ Free SSL certificate

---

## 🔧 Post-Deployment

### Access Your App
```
https://bfsi-loan-system.onrender.com
```

### Test Health Check
```bash
curl https://bfsi-loan-system.onrender.com/health
```

### View Logs
- Go to Render Dashboard
- Click on your service
- Click "Logs" tab

---

## 🎯 Testing the Deployed App

1. **Open the URL** in your browser
2. **Click "Start Application"**
3. **Use quick action**: "5L for 3 years"
4. **Enter KYC**: `Priya Sharma, PAN FGHIJ5678K, SALARIED`
5. **Download sanction letter** 🎉

---

## 🔄 Updating Your App

Just push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render **auto-deploys** within 2-3 minutes!

---

## 💡 Upgrading to Paid Plan

If you need:
- No sleep (24/7 uptime)
- More RAM (1GB+)
- Faster builds

Upgrade to **Starter Plan** ($7/month):
- Go to Render Dashboard
- Click your service → Settings
- Change plan to "Starter"

---

## 🐛 Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Verify Python version is 3.11
- Check Render logs for errors

### App Doesn't Start
- Verify `app.py` exists
- Check `gunicorn` is in requirements
- Ensure port binding uses `$PORT` env var

### 502 Bad Gateway
- App is sleeping (free tier)
- Wait 30 seconds for wake-up
- Or upgrade to paid plan

---

## 📊 Monitoring

### Built-in Metrics
Render provides:
- Request count
- Response times
- Error rates
- Memory usage

Access via Dashboard → Metrics tab

---

## 🎉 You're Live!

Your loan origination system is now:
- ✅ Deployed to production
- ✅ Accessible worldwide
- ✅ Auto-deploying on updates
- ✅ Free SSL certificate
- ✅ Health monitoring

**Share your URL and start processing loans!** 🚀
