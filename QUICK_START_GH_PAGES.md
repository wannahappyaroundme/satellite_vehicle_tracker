# 🚀 Quick Start: GitHub Pages Deployment

## Get Your Satellite Vehicle Tracker Live in 5 Minutes!

### Step 1: Create GitHub Repository
1. Go to [github.com](https://github.com) and sign in
2. Click "+" → "New repository"
3. Name: `satellite-vehicle-tracker`
4. Make it **Public** (required for free GitHub Pages)
5. Click "Create repository"

### Step 2: Push Your Code
```bash
# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/satellite-vehicle-tracker.git

# Push your code
git push -u origin main
```

### Step 3: Enable GitHub Pages
1. Go to your repository → "Settings"
2. Click "Pages" in the left sidebar
3. Source: "Deploy from a branch"
4. Branch: `gh-pages`
5. Click "Save"

### Step 4: Deploy!
```bash
# Run the deployment script
./deploy_gh_pages.sh
```

### Step 5: Access Your App! 🎉
Your application will be live at:
```
https://YOUR_USERNAME.github.io/satellite-vehicle-tracker
```

## 🔄 Automatic Updates
Every time you push to the `main` branch, GitHub Actions will automatically deploy your changes!

## 🛠️ Backend Deployment
For the backend API, you'll need to deploy it separately to services like:
- Railway (recommended)
- Heroku
- DigitalOcean App Platform
- Or run locally for development

## 📱 Features Available
- ✅ Interactive satellite imagery analysis
- ✅ Vehicle detection and classification
- ✅ Long-term parking analysis
- ✅ South Korea satellite data integration
- ✅ Airbnb-style hover cards
- ✅ Mobile-responsive design

## 🆘 Need Help?
Check the detailed guides:
- `GITHUB_PAGES_SETUP.md` - Complete setup guide
- `GITHUB_SETUP.md` - General GitHub setup
- `README.md` - Full documentation

Your Satellite Vehicle Tracker is ready to go live! 🛰️✨
