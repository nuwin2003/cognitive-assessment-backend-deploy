# Render Deployment Guide

## Prerequisites
- GitHub repository with your code
- MongoDB Atlas account (or other MongoDB hosting)
- Render account

## Steps to Deploy

### 1. Prepare MongoDB
- Create a MongoDB Atlas cluster (or use existing)
- Get your connection string: `mongodb+srv://user:password@cluster.mongodb.net/`
- Whitelist Render IP or allow all IPs (0.0.0.0/0)

### 2. Create Render Web Service
1. Go to [https://render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Fill in the details:
   - **Name**: `cognitive-assessment-backend` (or your choice)
   - **Environment**: Docker
   - **Region**: Choose closest to your users
   - **Branch**: main (or your deployment branch)
   - **Build Command**: Leave empty (Docker will handle it)
   - **Start Command**: Leave empty (Dockerfile has CMD)

### 3. Configure Environment Variables
In the Render dashboard, add these environment variables:

```
MONGODB_URI=mongodb+srv://username:password@your-cluster.mongodb.net/
DATABASE_NAME=dyslexia_app
```

### 4. Deploy
- Click "Create Web Service"
- Render will automatically build and deploy
- Monitor the build logs
- Once deployed, you'll get a URL like: `https://cognitive-assessment-backend.onrender.com`

## Important Notes

### Port Configuration
- Render automatically assigns a port via the `PORT` environment variable
- The Dockerfile/Uvicorn is configured to listen on 0.0.0.0:8000
- Render's reverse proxy handles the PORT assignment

### MongoDB Connection
- Ensure your MongoDB URI includes `mongodb+srv://` (not plain `mongodb://`)
- Make sure Render's IP is whitelisted in MongoDB Atlas Network Access
- For testing: temporarily allow `0.0.0.0/0` in MongoDB Atlas

### Health Checks
- Add a simple GET endpoint if needed:
```python
@app.get("/health")
async def health():
    return {"status": "ok"}
```

### Logs & Debugging
- View logs in Render dashboard: Settings → Logs
- Check build failures in Build Logs tab

## Troubleshooting

**"Can't connect to MongoDB"**
- Check MONGODB_URI environment variable is correct
- Verify IP whitelist in MongoDB Atlas
- Test connection locally with the same URI

**"Module not found"**
- Check requirements.txt has all dependencies
- Verify Python version compatibility (using 3.11)

**"Port already in use"**
- This shouldn't happen on Render, but verify Dockerfile uses dynamic PORT
