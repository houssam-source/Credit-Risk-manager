# 🚀 Deploy Credit Risk Management to Streamlit Cloud

## Overview
This guide will help you deploy the Credit Risk Management Dashboard to Streamlit Cloud using GitHub.

## Prerequisites
- GitHub account
- Streamlit Cloud account (free)
- Git installed on your local machine

## Step-by-Step Deployment Guide

### 1️⃣ Initialize Git Repository

```bash
# Navigate to project directory
cd "c:\Users\ROG\Desktop\credit risk management"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Credit Risk Management System"
```

### 2️⃣ Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `Credit-Risk-manager` (or your preferred name)
3. Set as **Public** (required for free Streamlit Cloud)
4. **Don't** initialize with README (we already have one)
5. Click "Create repository"

### 3️⃣ Push to GitHub

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/houssam-source/Credit-Risk-manager.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 4️⃣ Configure Streamlit Cloud

#### Option A: Deploy Directly from GitHub

1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub account (if not already connected)
4. Select your repository: `houssam-source/Credit-Risk-manager`
5. Branch: `main`
6. Main file path: `src/dashboard/app.py`
7. Runtime requirements file: `streamlit-requirements.txt`
8. Click "Deploy!"

#### Option B: Advanced Configuration (Recommended)

Create `.streamlit/config.toml` for production settings:

```toml
[server]
headless = true
port = $PORT
address = "localhost"
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### 5️⃣ Environment Variables Setup

In Streamlit Cloud dashboard, go to your app settings and add these secrets:

1. **API_URL** (optional if using external API):
   ```
   Value: https://your-api-url.herokuapp.com
   ```

2. **Other secrets** (as needed):
   ```
   API_KEY: your-secret-key
   ```

### 6️⃣ Access Your Deployed App

Once deployed, your app will be available at:
```
https://houssam-source-credit-risk-manager-app-xyz123.streamlit.app
```

## 📁 Important File Structure

```
credit-risk-management/
├── src/
│   └── dashboard/
│       ├── app.py              # Main Streamlit app ✅
│       ├── multipage.py        # Multi-page framework ✅
│       └── pages/
│           ├── home.py         ✅
│           ├── data_exploration.py ✅
│           ├── model_performance.py ✅
│           ├── predictions.py  ✅
│           └── feature_analysis.py ✅
├── streamlit-requirements.txt  # Dependencies for Streamlit Cloud ✅
├── .gitignore                  # Git ignore rules ✅
└── README.md                   # Project documentation
```

## ⚠️ Important Notes

### Model Files
**DO NOT commit large model files to GitHub** (Git LFS has limits on free plan).

**Solutions:**

1. **Option 1: Use Google Drive/Dropbox**
   - Upload models to cloud storage
   - Download on app startup
   - Add download script to dashboard

2. **Option 2: Use Streamlit Cloud's persistent storage** (paid feature)

3. **Option 3: Host API separately**
   - Deploy API to Heroku/Railway
   - Dashboard calls API via HTTP requests
   - Models stay with API server

### Data Files
- Keep sample data in `data/processed/` for demo
- Exclude large raw data files
- Use `.gitignore` rules (already configured)

## 🔧 Troubleshooting

### App won't start?
Check Streamlit Cloud logs for errors. Common issues:
- Wrong main file path (should be `src/dashboard/app.py`)
- Missing dependencies (check `streamlit-requirements.txt`)
- Import errors (verify all imports in your code)

### Models not loading?
Models are likely too large for GitHub. Use one of the solutions above.

### API connection fails?
- Ensure API is deployed and accessible
- Update `API_URL` environment variable
- Check CORS settings in API

## 🎯 Next Steps

1. ✅ Test local deployment first
2. ✅ Push to GitHub
3. ✅ Deploy to Streamlit Cloud
4. ✅ Configure environment variables
5. ✅ Share your app URL!

## 📚 Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Basics](https://docs.github.com/en/get-started)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/quickstart/secrets-management)

---

**Ready to deploy?** Follow the steps above and you'll have your credit risk dashboard live in minutes! 🚀
