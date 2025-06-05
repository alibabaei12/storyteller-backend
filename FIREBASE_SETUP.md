# Firebase Setup for StoryTeller

## 1. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select your existing StoryTeller project
3. Enable Firestore Database:
   - Go to **Firestore Database**
   - Click **Create database**
   - Choose **Start in test mode** (for development)
   - Select a location close to your users

## 2. Service Account Setup

1. Go to **Project Settings** → **Service accounts**
2. Click **Generate new private key**
3. Save the JSON file as `firebase-service-account.json` in the `storyteller-python` directory
4. **Important:** Add this file to `.gitignore` to avoid committing credentials

## 3. Local Development Setup

For local development, you have two options:

### Option A: Service Account File (Recommended for development)
```bash
# Set environment variable to point to your service account file
export GOOGLE_APPLICATION_CREDENTIALS="./firebase-service-account.json"
```

### Option B: Application Default Credentials
```bash
# Install Google Cloud CLI and authenticate
gcloud auth application-default login
```

## 4. Environment Variables

Update your `.env` file:
```env
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
```

## 5. Testing the Connection

Run this to test your Firebase connection:
```bash
cd storyteller-python
python3 -c "from app.firebase_service import firebase_service; print('Firebase connected successfully!')"
```

## 6. Production Deployment

For production (Render, Heroku, etc.):

1. **Don't upload the service account JSON file**
2. Instead, set environment variables:
   - `FIREBASE_PRIVATE_KEY` - The private key from your JSON file
   - `FIREBASE_CLIENT_EMAIL` - The client email from your JSON file
   - `FIREBASE_PROJECT_ID` - Your project ID

3. Update your production deployment with these environment variables

## 7. Firestore Security Rules

For development, you can use these permissive rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

**For production, implement proper security rules based on user authentication.**

## Troubleshooting

- **"Application Default Credentials not found"**: Make sure you've set up authentication properly
- **Permission denied**: Check your Firestore security rules
- **Module not found**: Make sure you've installed `firebase-admin` with `pip install firebase-admin`

## What's Next?

Once Firebase is configured:
1. Your app will automatically store new stories in Firestore
2. All user data will be persistent across deployments
3. You can view your data in the Firebase Console under Firestore Database

The app will now work with Firebase instead of local file storage! 