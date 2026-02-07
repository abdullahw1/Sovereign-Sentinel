# Deployment Guide for Render

## Quick Deploy

### Option 1: Using render.yaml (Recommended)
1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and create both services
6. Add environment variables in Render dashboard:
   - `OPENAI_API_KEY`
   - `YOU_API_KEY`

### Option 2: Manual Setup

#### Backend Deployment
1. Go to Render Dashboard
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: sovereign-sentinel-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `OPENAI_API_KEY` = your_openai_key
     - `YOU_API_KEY` = your_you_api_key

#### Frontend Deployment
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: sovereign-sentinel-frontend
   - **Environment**: Node
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Start Command**: `cd frontend && npm start`
   - **Environment Variables**:
     - `NEXT_PUBLIC_API_URL` = https://sovereign-sentinel-backend.onrender.com

## Environment Variables Required

### Backend
- `OPENAI_API_KEY` - Your OpenAI API key
- `YOU_API_KEY` - Your You.com API key

### Frontend
- `NEXT_PUBLIC_API_URL` - URL of your deployed backend (e.g., https://sovereign-sentinel-backend.onrender.com)

## Post-Deployment

1. Wait for both services to deploy (5-10 minutes)
2. Visit your frontend URL
3. The system will automatically connect to the backend
4. Test the demo by clicking "Run Risk Assessment"

## Troubleshooting

### Backend won't start
- Check that environment variables are set correctly
- Verify `requirements.txt` is in the root directory
- Check logs in Render dashboard

### Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` points to your backend URL
- Check CORS settings in `backend/app/main.py`
- Ensure backend is running and healthy

### Database/Data Issues
- The app uses JSON files in `backend/data/` directory
- These are committed to the repo and will be available on Render
- For production, consider using a proper database

## Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down will be slow (cold start)
- Consider upgrading to paid tier for production use
