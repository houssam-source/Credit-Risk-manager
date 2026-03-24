# 🔒 Security Quick Start Guide

## ⚡ Quick Setup (5 Minutes)

### Step 1: Generate Secure Configuration

Run the automated security setup script:

```bash
python scripts/security_setup.py
```

This will:
- ✅ Generate cryptographically secure API key
- ✅ Create SHA256 hashes for model integrity
- ✅ Create `.env` file with all settings
- ✅ Create Streamlit `secrets.toml`
- ✅ Validate your configuration

### Step 2: Review & Customize

Open the generated `.env` file and update:

```env
# Replace with your actual frontend domain
API_ALLOWED_ORIGINS=https://your-domain.com

# Verify API key was generated (should NOT be empty or placeholder)
API_KEY=long-random-string-generated-automatically
```

### Step 3: Deploy Securely

#### For Local Development:
```bash
# API Server
uvicorn src.api.server_model:app --host 127.0.0.1 --port 8000

# Dashboard
streamlit run src/dashboard/app.py
```

#### For Streamlit Cloud:
1. Go to https://share.streamlit.io
2. Select your app → Settings → Secrets
3. Add secrets from `.streamlit/secrets.example.toml`
4. Deploy!

---

## 📋 Security Checklist

### Before Production Deployment

- [ ] **Run security setup**
  ```bash
  python scripts/security_setup.py
  ```

- [ ] **Verify .env file**
  - [ ] API_KEY is a long random string (not default)
  - [ ] API_ENV=prod
  - [ ] API_ALLOWED_ORIGINS has your actual domains
  - [ ] Model hashes are generated

- [ ] **Update CORS origins**
  - Remove localhost entries
  - Add only trusted domains
  - No wildcards (*) allowed

- [ ] **Generate model hashes**
  ```bash
  python scripts/generate_model_hashes.py
  ```

- [ ] **Test API endpoints**
  - [ ] /docs disabled in production
  - [ ] /redoc disabled in production
  - [ ] /health returns minimal info
  - [ ] API key authentication works

- [ ] **Secure environment files**
  - [ ] .env NOT committed to Git
  - [ ] secrets.toml NOT committed to Git
  - [ ] File permissions restricted

---

## 🔐 Key Security Features

### What's Protected

| Feature | Protection | Status |
|---------|-----------|--------|
| API Authentication | X-API-Key header with timing-safe comparison | ✅ Enabled |
| CORS | Restricted origins, no wildcards | ✅ Configured |
| Request Size | 256KB limit (DoS protection) | ✅ Enabled |
| Security Headers | X-Frame-Options, X-Content-Type-Options, etc. | ✅ Added |
| Model Integrity | SHA256 hash verification | ✅ Enabled |
| Input Validation | Pydantic schemas with constraints | ✅ Active |
| Error Handling | Generic messages, detailed server logs | ✅ Configured |
| Production Mode | Docs disabled, minimal info | ✅ Available |

---

## 🆘 Troubleshooting

### Common Issues

**Problem: "Unauthorized" errors**
```bash
# Solution: Set API_KEY in .env
API_KEY=your-generated-key-here

# Or disable for local dev (NOT production!)
API_ENV=dev
```

**Problem: CORS errors**
```bash
# Solution: Add your frontend domain to allowed origins
API_ALLOWED_ORIGINS=https://your-actual-domain.com
```

**Problem: Model loading fails**
```bash
# Solution: Generate correct SHA256 hashes
python scripts/generate_model_hashes.py
```

---

## 🎯 Production Checklist

### Must-Have for Production

- ✅ **Strong API Key**: Minimum 32 characters, randomly generated
- ✅ **Production Mode**: `API_ENV=prod`
- ✅ **Restricted CORS**: Only your domains, no wildcards
- ✅ **Model Verification**: All SHA256 hashes configured
- ✅ **HTTPS**: SSL/TLS for API server
- ✅ **Environment Isolation**: Separate .env for each environment
- ✅ **Secret Rotation Plan**: Schedule regular key rotation

### Recommended Enhancements

- 🔒 Rate limiting (for high-traffic APIs)
- 🔒 Monitoring/alerting system
- 🔒 Regular security audits
- 🔒 Penetration testing
- 🔒 Dependency vulnerability scanning

---

## 📚 Additional Resources

- **Full Security Docs**: [SECURITY.md](./SECURITY.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Streamlit Secrets**: https://docs.streamlit.io/streamlit-community-cloud/get-started/quickstart/secrets-management
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/

---

## 🚀 Ready to Deploy?

1. ✅ Run `python scripts/security_setup.py`
2. ✅ Review and customize `.env` file
3. ✅ Test locally
4. ✅ Deploy to production
5. ✅ Monitor and maintain

**Your Credit Risk Management API is now secured! 🔒**

---

Last Updated: March 24, 2026
