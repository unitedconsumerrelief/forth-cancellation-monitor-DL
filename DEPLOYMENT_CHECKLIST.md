# 🚀 Render Deployment Checklist

## ✅ Pre-Deployment Setup

### 1. Local OAuth Setup
- [ ] Download `credentials.json` from Google Cloud Console
- [ ] Place `credentials.json` in project root
- [ ] Run `python app.py` to complete OAuth flow
- [ ] Verify `token.json` was created
- [ ] Test locally: `MODE=server python app.py`
- [ ] Test health: `python test_health.py`

### 2. Extract OAuth Credentials
- [ ] Run `python extract_oauth_credentials.py`
- [ ] Copy the three environment variables:
  - `GOOGLE_CLIENT_ID=...`
  - `GOOGLE_CLIENT_SECRET=...`
  - `GOOGLE_REFRESH_TOKEN=...`

### 3. Prepare Repository
- [ ] Create private GitHub repository
- [ ] Push code (exclude `credentials.json` and `token.json`)
- [ ] Verify these files are in `.gitignore`

## 🚀 Render Deployment

### 4. Deploy Single Web Service (Combined Mode)
- [ ] Create new Web Service in Render
- [ ] Connect GitHub repository
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `python app.py`
- [ ] Add environment variables:
  - [ ] `MODE=combined` (runs both health server and Gmail polling)
  - [ ] `SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...`
  - [ ] `SLACK_CHANNEL=forth-alerts`
  - [ ] `SLACK_USERNAME=Gmail Monitor`
  - [ ] `GMAIL_QUERY=from:noreply@forthcrm.com (subject:"Cancellation" OR subject:"Cancel" OR subject:"cancelled" OR subject:"cancelled") newer_than:7d`
  - [ ] `POLL_INTERVAL_SECONDS=60`
  - [ ] `TIMEZONE=Asia/Manila`
  - [ ] `RETURN_FULL_BODY=true`
  - [ ] `PORT=10000`
  - [ ] `GOOGLE_CLIENT_ID=...` (from step 2)
  - [ ] `GOOGLE_CLIENT_SECRET=...` (from step 2)
  - [ ] `GOOGLE_REFRESH_TOKEN=...` (from step 2)
- [ ] Deploy and note the URL

**Note**: Combined mode runs both health endpoint AND Gmail polling in one deployment!

### 6. UptimeRobot Setup
- [ ] Go to [UptimeRobot](https://uptimerobot.com/)
- [ ] Add new monitor:
  - [ ] Type: HTTP(s)
  - [ ] URL: `https://your-app.onrender.com/health`
  - [ ] Interval: 5 minutes
- [ ] Verify health checks are working

## 🧪 Testing

### 7. Verify Deployment
- [ ] Check Web Service logs for successful startup
- [ ] Check Background Worker logs for Gmail connection
- [ ] Test health endpoint: `curl https://your-app.onrender.com/health`
- [ ] Send test email matching Gmail query
- [ ] Verify message appears in Slack channel
- [ ] Check for any error messages in logs

## 🔧 Troubleshooting

### Common Issues
- [ ] **OAuth errors**: Verify environment variables are set correctly
- [ ] **No Slack posts**: Check webhook URL and Gmail query
- [ ] **Health check fails**: Verify Web Service is running
- [ ] **Worker not polling**: Check Background Worker logs
- [ ] **Database errors**: Ensure SQLite file is persistent

### Logs to Check
- [ ] Web Service logs in Render dashboard
- [ ] Background Worker logs in Render dashboard
- [ ] UptimeRobot monitor status

## ✅ Success Criteria

- [ ] Health endpoint returns `{"ok": true}`
- [ ] Background worker connects to Gmail successfully
- [ ] Test emails are posted to Slack
- [ ] No duplicate messages (deduplication working)
- [ ] UptimeRobot shows service as up
- [ ] Service runs on Render free tier without issues

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Render deployment logs
3. Verify all environment variables are set
4. Test locally first before deploying

