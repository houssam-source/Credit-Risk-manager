# 🚀 Quick Deploy to Streamlit Cloud

## Step 1: Push to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/houssam-source/Credit-Risk-manager.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 2: Deploy on Streamlit Cloud

1. **Go to** https://share.streamlit.io
2. **Click** "New app"
3. **Connect** your GitHub account
4. **Select** your repository: `houssam-source/Credit-Risk-manager`
5. **Configure:**
   - Branch: `main`
   - Main file path: `src/dashboard/app.py`
   - Requirements file: `streamlit-requirements.txt`
6. **Click** "Deploy!"

## Step 3: Configure Secrets (Optional)

In Streamlit Cloud dashboard, add these secrets if using external API:

- `API_URL`: Your deployed API endpoint
- `API_KEY`: Your API key (if required)

## ✅ Done!

Your app will be live at:
```
https://houssam-source-credit-risk-manager-app-xyz123.streamlit.app
```

---

## ⚠️ Important Notes

### Model Files
This repository excludes large model files (`.pkl`, `.h5`). For production deployment:

**Option 1: Use Sample Data for Demo**
- Dashboard will work with simulated predictions
- No models needed for basic demo

**Option 2: Host Models Externally**
- Upload models to Google Drive/Dropbox
- Download on app startup
- Or deploy API separately (Heroku/Railway)

**Option 3: Use Git LFS** (for smaller models)
```bash
git lfs install
git lfs track "src/models/outputs/*.pkl"
git add .gitattributes
git commit -m "Add model files with LFS"
git push
```

### Data Files
Large CSV files are excluded. Keep only sample data for demo purposes.

---

## 🔗 Useful Links

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [GitHub Setup Help](https://docs.github.com/en/get-started)
