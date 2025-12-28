# 🚀 CCTV Pro - Railway Deployment Guide

## ✅ Files Ready for Deployment

Your project is now configured for Railway deployment with:
- ✅ `Procfile` - Tells Railway how to run your app
- ✅ `runtime.txt` - Specifies Python 3.11
- ✅ `requirements.txt` - All dependencies listed
- ✅ `railway.json` - Railway-specific configuration
- ✅ `.gitignore` - Excludes unnecessary files

---

## 🎯 Deploy to Railway (5 Minutes)

### Step 1: Sign Up for Railway

1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Sign in with **GitHub** (easiest)
4. Authorize Railway to access your repos

### Step 2: Deploy Your App

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: **`mahabisoufiane/cctv`**
4. Railway will:
   - ✅ Detect it's a Flask app
   - ✅ Read `Procfile` and `requirements.txt`
   - ✅ Install dependencies
   - ✅ Start your app

### Step 3: Wait for Deployment

- Watch the build logs (2-3 minutes)
- Look for: **"✓ Deployment successful"**
- Railway will give you a URL

### Step 4: Get Your Public URL

1. In Railway dashboard, click **"Settings"**
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. You'll get a URL like:
   ```
   https://cctv-production-xxxx.up.railway.app
   ```

---

## 🔑 Set Environment Variables (Important!)

### In Railway Dashboard:

1. Go to **"Variables"** tab
2. Add these variables:

```
ACCESS_TOKEN=cctv-demo-2025-secret
SECRET_KEY=your-random-secret-key-here
```

**To generate a strong SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

3. Click **"Deploy"** to apply changes

---

## 🌐 Share Your Website

### Public Access Link (with token):
```
https://your-app.up.railway.app/access?token=cctv-demo-2025-secret
```

### Send to Clients:
```
Bonjour,

Voici le lien pour accéder à notre site CCTV Pro:
https://your-app.up.railway.app/access?token=cctv-demo-2025-secret

Le site sera accessible pendant 30 jours après connexion.

Cordialement,
CCTV Pro Team
```

---

## 🧪 Test Your Deployment

1. **Visit your Railway URL** (without token)
   - Should redirect to `/access` page ✅

2. **Test access page:**
   - Enter token: `cctv-demo-2025-secret`
   - Should login successfully ✅

3. **Test with direct link:**
   ```
   https://your-app.up.railway.app/access?token=cctv-demo-2025-secret
   ```
   - Should auto-login ✅

4. **Test all features:**
   - ✅ Calculator works
   - ✅ Contact form submits
   - ✅ Language switching works
   - ✅ Mobile responsive

---

## 🔄 Auto-Deploy Updates

**Good news:** Railway auto-deploys when you push to GitHub!

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push origin master

# Railway automatically:
# 1. Detects the push
# 2. Rebuilds your app
# 3. Deploys new version
# 4. URL stays the same!
```

---

## 💰 Railway Free Tier

✅ **$5 free credits per month**
✅ **500 hours of runtime**
✅ **1GB RAM**
✅ **1GB storage**
✅ **Free HTTPS/SSL**
✅ **Custom domains**
✅ **No credit card required**

**Perfect for demos and small projects!**

---

## 🎨 Custom Domain (Optional)

Want `cctv-pro.com` instead of Railway subdomain?

1. Buy domain (Namecheap, GoDaddy, etc.)
2. In Railway: **Settings → Domains**
3. Add custom domain
4. Update DNS records (Railway gives you instructions)
5. Wait 5-60 minutes for DNS propagation

---

## 🐛 Troubleshooting

### Problem: Build Failed
**Solution:** Check Railway build logs. Usually missing dependency.

### Problem: App Crashes
**Solution:** 
- Check Railway logs: **Deployments → View Logs**
- Verify environment variables are set

### Problem: Database Not Working
**Solution:** Railway creates SQLite automatically. Check file permissions.

### Problem: Token Not Working
**Solution:** 
- Verify `ACCESS_TOKEN` environment variable is set
- Check for typos in token

---

## 📊 Monitor Your App

**In Railway Dashboard:**
- ✅ View live logs
- ✅ See deployment history
- ✅ Monitor resource usage
- ✅ Check uptime

---

## 🔐 Security Checklist

✅ Change default `ACCESS_TOKEN`
✅ Set strong `SECRET_KEY`
✅ Use HTTPS (Railway provides this)
✅ Don't commit `.env` files
✅ Rotate tokens periodically

---

## 🚀 Alternative Deployment Options

### If Railway doesn't work:

**Option 2: Render.com**
- Free tier: 750 hours/month
- Very similar to Railway
- https://render.com

**Option 3: PythonAnywhere**
- Always free tier
- Python-focused
- https://pythonanywhere.com

**Option 4: Heroku**
- Classic option (not free anymore)
- Reliable but costs $5-7/month

---

## ✨ Success Checklist

✅ Project deployed to Railway
✅ Environment variables set
✅ Public URL generated
✅ Access page loads
✅ Token authentication works
✅ All features tested
✅ Shared link with clients

---

## 📱 Share Your Success!

Your CCTV Pro website is now live on the internet! 🎉

**Your public link:**
```
https://your-app.up.railway.app/access?token=cctv-demo-2025-secret
```

**Features:**
- ✅ Beautiful modern design
- ✅ Token-protected access
- ✅ Price calculator
- ✅ Contact forms
- ✅ Multi-language support
- ✅ Mobile responsive
- ✅ Admin dashboard
- ✅ 24/7 online

---

## 🆘 Need Help?

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

**Your Project:**
- GitHub: https://github.com/mahabisoufiane/cctv
- Version: v0.2.1

---

**Deployed on:** December 28, 2025
**Status:** ✅ Ready for Production
**Cost:** $0 (FREE)

🎉 **Congratulations! Your website is live!**
