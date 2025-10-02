# Gmail → Slack Monitor

A Python service that polls a Gmail inbox using a Gmail search query and posts matching messages to Slack via Incoming Webhook. Designed to run reliably on Render.com with UptimeRobot keep-alive support.

## Features

- 🔍 **Gmail Polling**: Uses Gmail API with OAuth2 authentication
- 📱 **Slack Integration**: Posts formatted messages via Incoming Webhook
- 🔄 **Deduplication**: SQLite-based state tracking prevents duplicate posts
- 🏥 **Health Monitoring**: Flask health endpoint for uptime monitoring
- 🌍 **Timezone Support**: Configurable timezone for message timestamps
- 🚀 **Render.com Ready**: Optimized for free tier deployment
- 🔧 **Triple Mode**: Server mode (health checks), Worker mode (polling), or Combined mode (both)

## Project Structure

```
gmail-slack-monitor/
├── app.py                 # Main application (Flask + Gmail polling)
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration (create this)
├── credentials.json       # Google OAuth credentials (user-provided)
├── token.json            # Generated OAuth token (auto-created)
├── state.db              # SQLite database for deduplication (auto-created)
└── README.md             # This file
```

## Setup Instructions

### 1. Slack Incoming Webhook

1. Go to your Slack workspace
2. Navigate to **Apps** → **Incoming Webhooks**
3. Click **Add to Slack**
4. Choose the target channel (e.g., `#alerts`)
5. Copy the webhook URL (format: `https://hooks.slack.com/services/XXX/YYY/ZZZ`)

### 2. Gmail API OAuth Client

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Gmail API**:
   - Go to **APIs & Services** → **Library**
   - Search for "Gmail API" and enable it
4. Create OAuth credentials:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - Choose **Desktop application**
   - Download the JSON file and rename it to `credentials.json`
   - Place it in your project root

**Important for Render Deployment**: The app supports both file-based credentials (local development) and environment variable credentials (production deployment). For Render, you'll extract the credentials from the JSON files and set them as environment variables.

### 3. Environment Configuration

Create a `.env` file in your project root:

```env
# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
SLACK_CHANNEL=#alerts
SLACK_USERNAME=Gmail Monitor

# Gmail Configuration
GMAIL_QUERY=label:inbox is:unread newer_than:7d

# Polling Configuration
POLL_INTERVAL_SECONDS=60
TIMEZONE=Asia/Manila

# Optional Settings
RETURN_FULL_BODY=false
MODE=server   # 'server' (Flask healthcheck) or 'worker' (polling loop)

# Server Configuration (for Render deployment)
PORT=10000
```

### 4. Local Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **First run (OAuth authorization)**:
   ```bash
   python app.py
   ```
   - This will open a browser for Gmail OAuth authorization
   - Grant permissions and the `token.json` file will be created
   - You can stop the process after authorization

3. **Test the service**:
   ```bash
   # Test health endpoint
   MODE=server python app.py
   # In another terminal: curl http://localhost:10000/health
   
   # Test polling worker
   MODE=worker python app.py
   ```

4. **Send a test email** that matches your `GMAIL_QUERY`
5. **Verify** the message appears in your Slack channel

## Deployment to Render.com

### 1. Prepare Repository

1. Create a **private** GitHub repository
2. Push your code with these files:
   - `app.py`
   - `requirements.txt`
   - `extract_oauth_credentials.py` (helper script)
   - `credentials.json` (for local OAuth setup only)
   - `token.json` (generated from local OAuth setup only)

**Note**: Do NOT include `credentials.json` or `token.json` in your production repository. These are only needed for local OAuth setup.

### 2. Extract OAuth Credentials for Render

1. **Run locally first** to generate `token.json`:
   ```bash
   python app.py
   # Complete OAuth flow in browser
   ```

2. **Extract credentials** for Render deployment:
   ```bash
   python extract_oauth_credentials.py
   ```

3. **Copy the output** - you'll get environment variables like:
   ```
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   GOOGLE_REFRESH_TOKEN=your_refresh_token_here
   ```

### 3. Deploy Single Web Service (Combined Mode)

1. In Render dashboard, create **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment Variables**: Add all variables from your `.env` file PLUS the OAuth credentials from step 2
   - **Environment**: Set `MODE=combined` (runs both health server and Gmail polling)
4. Deploy and note the URL (e.g., `https://your-app.onrender.com`)

**Note**: The combined mode runs both the health endpoint AND Gmail polling in a single deployment, saving costs!

### 4. UptimeRobot Setup

1. Go to [UptimeRobot](https://uptimerobot.com/)
2. Add a new monitor:
   - **Monitor Type**: HTTP(s)
   - **URL**: Your Render web service URL + `/health`
   - **Monitoring Interval**: 5 minutes
3. This keeps your free tier Render service alive

## Configuration Options

### Gmail Query Examples

```env
# Unread emails from last 7 days
GMAIL_QUERY=label:inbox is:unread newer_than:7d

# Emails from specific sender
GMAIL_QUERY=from:alerts@example.com is:unread

# Emails with specific subject
GMAIL_QUERY=subject:"URGENT" is:unread

# Emails with attachments
GMAIL_QUERY=has:attachment is:unread newer_than:1d

# Multiple conditions
GMAIL_QUERY=label:inbox from:system@company.com subject:"Alert" is:unread newer_than:3d
```

### Polling Configuration

```env
# Poll every 30 seconds (more frequent)
POLL_INTERVAL_SECONDS=30

# Poll every 5 minutes (less frequent)
POLL_INTERVAL_SECONDS=300

# Include full email body in Slack
RETURN_FULL_BODY=true
```

### Timezone Support

```env
# Common timezones
TIMEZONE=UTC
TIMEZONE=America/New_York
TIMEZONE=Europe/London
TIMEZONE=Asia/Tokyo
TIMEZONE=Asia/Manila
TIMEZONE=Australia/Sydney
```

## Security Best Practices

1. **Keep credentials private**:
   - Never commit `credentials.json`, `token.json`, or `.env` to public repos
   - Use private GitHub repositories for deployment

2. **Minimal permissions**:
   - Gmail API only requests read-only access
   - OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`

3. **Environment variables**:
   - Store sensitive data in Render environment variables
   - Use different webhook URLs for different environments

4. **Rate limiting**:
   - Gmail API has quotas (250 quota units per user per second)
   - Default polling interval (60s) is well within limits

## Troubleshooting

### No Slack Posts
- ✅ Check `SLACK_WEBHOOK_URL` is correct
- ✅ Verify `GMAIL_QUERY` matches your emails
- ✅ Check worker logs in Render dashboard
- ✅ Test webhook manually: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test"}' YOUR_WEBHOOK_URL`

### OAuth Errors
- ✅ Verify `credentials.json` is OAuth Desktop client type
- ✅ Delete `token.json` and re-run OAuth flow
- ✅ Check Google Cloud Console project has Gmail API enabled

### Wrong Timezone
- ✅ Use valid IANA timezone name in `TIMEZONE` env var
- ✅ Check [pytz documentation](https://pythonhosted.org/pytz/) for valid names

### Duplicate Messages
- ✅ Ensure `state.db` file is persistent (not recreated on restart)
- ✅ Check SQLite table `processed` exists and has data
- ✅ Verify worker and server are using same database file

### Render Deployment Issues
- ✅ Check build logs for dependency installation errors
- ✅ Verify all environment variables are set
- ✅ Ensure `MODE` is set correctly (server vs worker)
- ✅ Check worker logs for Gmail API errors

## Health Endpoint

The service provides a health check endpoint at `/health`:

```bash
curl https://your-app.onrender.com/health
```

Response:
```json
{
  "ok": true,
  "time": "2024-01-15T10:30:45+08:00",
  "timezone": "Asia/Manila",
  "mode": "server"
}
```

## Future Enhancements

- **Slack Bot API**: Replace webhooks with bot API for richer interactions
- **Gmail Push Notifications**: Use Pub/Sub instead of polling for real-time updates
- **Multiple Queries**: Support multiple Gmail queries with different Slack channels
- **Message Filtering**: Advanced filtering based on email content
- **Metrics**: Add Prometheus metrics for monitoring
- **Web UI**: Simple web interface for configuration

## License

MIT License - feel free to modify and distribute.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Render deployment logs
3. Test locally first before deploying
4. Verify all environment variables are set correctly