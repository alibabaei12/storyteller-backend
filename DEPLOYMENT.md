# Production Deployment Guide

## Firebase Environment Variables for Production

**NEVER** commit the `firebase-service-account.json` file to git. Instead, use environment variables.

### Step 1: Extract Credentials from Your JSON File

Open your `firebase-service-account.json` file and extract these values:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  ...
}
```

### Step 2: Set Environment Variables in Your Deployment Platform

#### For Render.com:
1. Go to your app dashboard
2. Click **Environment** tab
3. Add these environment variables:

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
OPENAI_API_KEY=your-openai-api-key
```

#### For Heroku:
```bash
heroku config:set FIREBASE_PROJECT_ID=your-project-id
heroku config:set FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
heroku config:set FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
heroku config:set OPENAI_API_KEY=your-openai-api-key
```

#### For Vercel:
```bash
vercel env add FIREBASE_PROJECT_ID
vercel env add FIREBASE_PRIVATE_KEY
vercel env add FIREBASE_CLIENT_EMAIL
vercel env add OPENAI_API_KEY
```

### Step 3: Update Frontend Environment Variables

In your React app's production environment, make sure you have:

```env
REACT_APP_API_URL=https://your-backend-url.onrender.com
REACT_APP_FIREBASE_API_KEY=your-firebase-web-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef
```

### Step 4: Test Production Setup

Your app will now:
- ✅ Use environment variables in production
- ✅ Use the JSON file in development
- ✅ Keep credentials secure and out of git

### Important Notes:

1. **Private Key Format**: Make sure the private key includes `\n` for newlines
2. **No JSON File Needed**: Production won't use the JSON file at all
3. **Secure**: Credentials are only stored in your deployment platform
4. **Easy Updates**: Change credentials without code changes

### Verification

After deployment, check your logs for:
```
[Firebase] Initialized with environment credentials for project: your-project-id
```

This confirms Firebase is working with environment variables in production! 