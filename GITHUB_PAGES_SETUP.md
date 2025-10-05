# GitHub Pages Deployment Guide

## 🚀 Deploy Your Satellite Vehicle Tracker to GitHub Pages

### Step 1: Create GitHub Repository

1. **Go to GitHub**: Visit [github.com](https://github.com) and sign in
2. **Create New Repository**: 
   - Click the "+" icon → "New repository"
   - Name: `satellite-vehicle-tracker`
   - Make it **Public** (required for free GitHub Pages)
   - Don't initialize with README (we already have files)

### Step 2: Push Your Code to GitHub

```bash
# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/satellite-vehicle-tracker.git

# Push your code
git push -u origin main
```

### Step 3: Enable GitHub Pages

1. **Go to Repository Settings**:
   - Click on your repository → "Settings" tab
   
2. **Navigate to Pages**:
   - In the left sidebar, click "Pages"
   
3. **Configure Source**:
   - Source: "Deploy from a branch"
   - Branch: `gh-pages` (this will be created automatically)
   - Folder: `/ (root)`
   - Click "Save"

### Step 4: Deploy to GitHub Pages

#### Option A: Quick Deploy (Recommended)
```bash
# Run the deployment script
./deploy_gh_pages.sh
```

#### Option B: Manual Deploy
```bash
# Install dependencies
npm install

# Build the application
npm run build

# Deploy to GitHub Pages
npm run deploy
```

### Step 5: Access Your Application

After deployment (takes 2-5 minutes), your application will be available at:
```
https://YOUR_USERNAME.github.io/satellite-vehicle-tracker
```

## 🔧 Configuration Details

### Frontend Configuration
The `package.json` has been configured with:
```json
{
  "homepage": "https://YOUR_USERNAME.github.io/satellite-vehicle-tracker",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

### API Configuration
Update the API URL in `src/services/api.ts`:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://your-backend-domain.com/api'  // Replace with your backend URL
    : 'http://localhost:5000/api');
```

## 🚀 Automated Deployment with GitHub Actions

### Enable GitHub Actions
1. **Go to Repository Settings** → "Actions" → "General"
2. **Enable Actions**: Allow all actions and reusable workflows
3. **Save settings**

### GitHub Actions Workflow
The `.github/workflows/gh-pages.yml` file will automatically:
- Build your React app on every push to main
- Deploy to GitHub Pages
- Handle all the deployment process

### Manual Trigger
You can also manually trigger deployment:
1. Go to your repository → "Actions" tab
2. Select "Deploy to GitHub Pages"
3. Click "Run workflow"

## 🌐 Backend Deployment Options

Since GitHub Pages only hosts static files, you'll need to deploy your backend separately:

### Option 1: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy backend
cd backend
railway deploy
```

### Option 2: Heroku
```bash
# Install Heroku CLI
# Create Procfile in backend/
echo "web: python app.py" > backend/Procfile

# Deploy
cd backend
heroku create your-app-name
git subtree push --prefix backend heroku main
```

### Option 3: DigitalOcean App Platform
1. Connect your GitHub repository
2. Configure build settings for Python
3. Deploy automatically

### Option 4: Local Development
For development, run the backend locally:
```bash
cd backend
python app.py
```

## 🔐 Environment Variables

### For Frontend (GitHub Pages)
Set these in your repository secrets:
1. Go to Repository Settings → "Secrets and variables" → "Actions"
2. Add these secrets:
   - `REACT_APP_API_URL`: Your backend API URL
   - `REACT_APP_GOOGLE_MAPS_API_KEY`: Your Google Maps API key

### For Backend
Set these in your hosting platform:
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string
- `GOOGLE_MAPS_API_KEY`: Google Maps API key

## 📱 Mobile Responsiveness

Your application is fully responsive and works on:
- ✅ Desktop computers
- ✅ Tablets
- ✅ Mobile phones
- ✅ All modern browsers

## 🔄 Updating Your Deployment

### Automatic Updates
Every time you push to the `main` branch:
1. GitHub Actions will automatically build and deploy
2. Changes will be live in 2-5 minutes

### Manual Updates
```bash
# Make your changes
git add .
git commit -m "Update application"
git push origin main

# Or use the deployment script
./deploy_gh_pages.sh
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. 404 Error on GitHub Pages
- Check if the repository is public
- Verify GitHub Pages is enabled in Settings
- Wait 5-10 minutes for deployment

#### 2. API Calls Not Working
- Update `REACT_APP_API_URL` in your environment
- Ensure your backend is deployed and accessible
- Check CORS settings in your backend

#### 3. Build Failures
- Check for TypeScript errors: `npm run lint`
- Verify all dependencies are installed: `npm install`
- Check the Actions tab for detailed error logs

#### 4. Styling Issues
- Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
- Check if all CSS files are loading correctly
- Verify build output in the `build` folder

## 📊 Monitoring and Analytics

### GitHub Pages Analytics
1. Go to Repository Settings → "Pages"
2. Enable "GitHub Pages Analytics" (if available)

### Custom Analytics
Add Google Analytics or other tracking:
```typescript
// In frontend/src/index.tsx
import ReactGA from 'react-ga';

ReactGA.initialize('YOUR_GA_TRACKING_ID');
ReactGA.pageview(window.location.pathname + window.location.search);
```

## 🎯 Next Steps

1. **Deploy your application** using the steps above
2. **Share your GitHub Pages URL** with users
3. **Deploy your backend** to a hosting service
4. **Update API URLs** to point to your backend
5. **Test everything** to ensure it works correctly

## 🔗 Useful Links

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

Your Satellite Vehicle Tracker will be live on GitHub Pages! 🛰️✨
