# 🔐 Gmail OAuth Setup Guide for reporting@unitedconsumerrelief.com

## 📋 **Overview**
This guide will help you set up Gmail OAuth authentication for the `reporting@unitedconsumerrelief.com` account so the monitoring service can read emails from `noreply@forthcrm.com`.

---

## 🚀 **Step 1: Google Cloud Console Setup**

### 1.1 Create or Select Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **Sign in** with an account that has admin access to `unitedconsumerrelief.com`
3. **Create a new project** OR **select existing project**:
   - Click the project dropdown at the top
   - Click "New Project" or select existing one
   - Name: "Forth CRM Email Monitor" (or similar)

### 1.2 Enable Gmail API
1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for **"Gmail API"**
3. Click on **Gmail API**
4. Click **"Enable"**
5. Wait for it to be enabled (usually instant)

---

## 🔑 **Step 2: Create OAuth 2.0 Credentials**

### 2.1 Navigate to Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"OAuth client ID"**

### 2.2 Configure OAuth Consent Screen (if first time)
1. If prompted, click **"Configure Consent Screen"**
2. Choose **"External"** (unless you have Google Workspace)
3. Fill in required fields:
   - **App name**: "Forth CRM Email Monitor"
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **"Save and Continue"**
5. Skip **Scopes** for now, click **"Save and Continue"**
6. Add your email as a **Test user**, click **"Save and Continue"**
7. Review and click **"Back to Dashboard"**

### 2.3 Create OAuth Client
1. Go back to **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. **Application type**: Select **"Desktop application"**
4. **Name**: "Forth CRM Monitor Desktop"
5. Click **"Create"**
6. **Download the JSON file** - this is your `credentials.json`
7. **Save it** in your project folder

---

## 🔐 **Step 3: OAuth Flow Setup**

### 3.1 Prepare Your Environment
1. **Place `credentials.json`** in your project folder
2. **Create `.env` file** with your configuration:
   ```env
   # Slack Configuration
   SLACK_WEBHOOK_URL=YOUR_WEBHOOK_URL_HERE
   SLACK_CHANNEL=forth-alerts
   SLACK_USERNAME=Gmail Monitor
   
   # Gmail Configuration
   GMAIL_QUERY=from:noreply@forthcrm.com (subject:"Cancellation" OR subject:"Cancel" OR subject:"cancelled" OR subject:"cancelled") newer_than:7d
   
   # Polling Configuration
   POLL_INTERVAL_SECONDS=60
   TIMEZONE=Asia/Manila
   RETURN_FULL_BODY=true
   MODE=server
   PORT=10000
   ```

### 3.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.3 Run OAuth Flow
1. **Open terminal/command prompt** in your project folder
2. **Run the OAuth flow**:
   ```bash
   python app.py
   ```
3. **Browser will open** - sign in with `reporting@unitedconsumerrelief.com`
4. **Grant permissions** when prompted
5. **Close browser** when complete
6. **Check for `token.json`** file created in your project folder

---

## ✅ **Step 4: Verify Setup**

### 4.1 Test Health Endpoint
```bash
MODE=server python app.py
```
In another terminal:
```bash
python test_health.py
```

### 4.2 Test Gmail Connection
```bash
MODE=worker python app.py
```
- Should show "Gmail service initialized successfully"
- Should start polling for emails

### 4.3 Extract Credentials for Render
```bash
python extract_oauth_credentials.py
```
- Copy the environment variables for Render deployment

---

## 🚀 **Step 5: Deploy to Render**

### 5.1 Prepare Repository
1. **Create private GitHub repository**
2. **Push your code** (exclude `credentials.json` and `token.json`)
3. **Include**:
   - `app.py`
   - `requirements.txt`
   - `extract_oauth_credentials.py`
   - `DEPLOYMENT_CHECKLIST.md`

### 5.2 Deploy Web Service
1. **Create Web Service** in Render
2. **Connect GitHub repository**
3. **Add environment variables**:
   - All variables from your `.env` file
   - OAuth credentials from step 4.3
   - `MODE=server`

### 5.3 Deploy Background Worker
1. **Create Background Worker** in Render
2. **Same repository** as Web Service
3. **Same environment variables** as Web Service
4. **Change** `MODE=worker`

---

## 🔧 **Step 6: UptimeRobot Setup**

1. Go to [UptimeRobot](https://uptimerobot.com/)
2. **Add new monitor**:
   - **Type**: HTTP(s)
   - **URL**: `https://your-app.onrender.com/health`
   - **Interval**: 5 minutes
3. **Verify** health checks are working

---

## 🧪 **Step 7: Test with Real Email**

1. **Send a test email** from Forth CRM to `reporting@unitedconsumerrelief.com`
2. **Check Slack** for the notification
3. **Verify** the message format and content

---

## ❗ **Important Notes**

### Security
- **Keep `credentials.json` and `token.json` private**
- **Don't commit them to public repositories**
- **Use environment variables in production**

### Permissions
- **Gmail API scope**: `https://www.googleapis.com/auth/gmail.readonly`
- **Read-only access** - cannot modify emails
- **Only reads emails** matching your query

### Troubleshooting
- **OAuth errors**: Delete `token.json` and re-run OAuth flow
- **Permission denied**: Check if `reporting@unitedconsumerrelief.com` has Gmail API access
- **No emails found**: Verify Gmail query and check if emails exist

---

## 📞 **Support**

If you encounter issues:
1. **Check the troubleshooting section**
2. **Verify all steps completed correctly**
3. **Test locally before deploying**
4. **Check Render logs for errors**

---

## ✅ **Success Criteria**

- [ ] Google Cloud Console project created
- [ ] Gmail API enabled
- [ ] OAuth credentials downloaded (`credentials.json`)
- [ ] OAuth flow completed with `reporting@unitedconsumerrelief.com`
- [ ] `token.json` file created
- [ ] Health endpoint working
- [ ] Gmail connection successful
- [ ] Deployed to Render (Web Service + Worker)
- [ ] UptimeRobot monitoring active
- [ ] Real Forth CRM emails posting to Slack

**You're ready to start monitoring Forth CRM cancellation emails!** 🎉
