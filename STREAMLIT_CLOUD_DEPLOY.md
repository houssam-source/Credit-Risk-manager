# 🚀 Deploy to Streamlit Cloud - Step by Step

## ✅ Prerequisites Complete

- [x] GitHub repository created: `houssam-source/Credit-Risk-manager`
- [x] Code pushed to GitHub
- [x] Streamlit configuration added (`.streamlit/config.toml`)
- [x] Requirements file ready (`streamlit-requirements.txt`)

## 📋 Deployment Steps

### Step 1: Go to Streamlit Cloud

**Visit:** https://share.streamlit.io

### Step 2: Sign In / Create Account

Choose one of these options:
- **Sign in with GitHub** (Recommended - easiest)
- **Sign in with Google**
- **Create new account**

### Step 3: Create New App

1. Click the **"New app"** button (or "Deploy an app" if first time)
2. You'll see a form with three fields

### Step 4: Configure Your App

Fill in the deployment form:

```
Repository: houssam-source/Credit-Risk-manager
Branch: main
Main file path: src/dashboard/app.py
```

**Advanced settings** (optional):
- Leave default settings
- No custom environment variables needed for basic deployment

### Step 5: Deploy!

1. Click **"Deploy!"** button
2. Wait 2-5 minutes for build and deployment
3. Watch the deployment logs in real-time

### Step 6: Access Your Live App

Once deployed, you'll get a URL like:
```
https://houssam-source-credit-risk-manager-app-xyz123.streamlit.app
```

You can also:
- Click **"Open app"** from the Streamlit Cloud dashboard
- Share the URL with others
- Access it from any device

## 🔧 Troubleshooting

### Build Failed?

**Common issues:**

1. **Missing dependencies**
   - Check `streamlit-requirements.txt` includes all packages
   - Verify package versions are compatible

2. **Import errors**
   - Ensure all imports are correct
   - Check that modules exist in your repository

3. **Config errors**
   - Verify `.streamlit/config.toml` syntax is valid
   - Remove any problematic configurations

### App Won't Load?

**Check these:**

1. **Model files missing**
   - Models are excluded from Git (too large)
   - Dashboard will use simulated predictions
   - For real predictions, deploy API separately

2. **Port configuration**
   - Don't hardcode port numbers
   - Streamlit Cloud manages ports automatically

3. **Headless mode**
   - Already configured in `.streamlit/config.toml`
   - Required for cloud deployment

## 📊 What Gets Deployed

✅ **Included:**
- Dashboard code (`src/dashboard/`)
- API server code (`src/api/`)
- Configuration files
- Dependencies list
- Documentation

❌ **Excluded:**
- Large model files (`.pkl`, `.h5`)
- Raw data files (CSV > 100MB)
- Cache files
- Virtual environment

## 🎯 Post-Deployment Checklist

After successful deployment:

- [ ] Test all dashboard pages
- [ ] Verify visualizations load correctly
- [ ] Check predictions page works
- [ ] Test on mobile device
- [ ] Share app URL with team

## 🔗 Useful Links

- **Your Repository:** https://github.com/houssam-source/Credit-Risk-manager
- **Streamlit Docs:** https://docs.streamlit.io
- **Community Forum:** https://discuss.streamlit.io
- **Troubleshooting Guide:** https://docs.streamlit.io/knowledge-base/tutorials/deploy

## 💡 Pro Tips

1. **Automatic Updates**
   - Every push to `main` branch triggers auto-deployment
   - No manual redeployment needed

2. **Custom Domain** (Paid feature)
   - Connect your own domain
   - Professional branding

3. **Secrets Management**
   - Add API keys in Streamlit Cloud dashboard
   - Navigate to: Settings → Secrets
   - Access via `st.secrets["key_name"]`

4. **Performance**
   - Use `@st.cache_data` for expensive computations
   - Already implemented in dashboard pages

## 🆘 Need Help?

If you encounter issues:

1. Check deployment logs in Streamlit Cloud
2. Review error messages carefully
3. Search Streamlit community forum
4. Check GitHub issues for similar problems
5. Contact Streamlit support (for paid plans)

---

**Ready to deploy?** Follow the steps above and your Credit Risk Dashboard will be live in minutes! 🎉
