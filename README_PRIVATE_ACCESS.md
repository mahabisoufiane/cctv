# 🔐 Private Access Setup - CCTV Pro v0.2.1

## Overview
Your website is now protected with token-based access. Only people with the secret token can view the site.

---

## 🎯 How It Works

1. **User visits your site** → Redirected to `/access` page
2. **User enters token** → System validates
3. **If correct** → Access granted for 30 days (stored in session)
4. **If incorrect** → Error message, try again

---

## 🔑 Default Token

```
cctv-demo-2025-secret
```

**⚠️ IMPORTANT: Change this token before sharing publicly!**

---

## 🔗 Sharing Access Links

### Method 1: Share Token Only
Give clients the token:
```
Token: cctv-demo-2025-secret
```
They visit your site and enter it manually.

### Method 2: Share Direct Link (Recommended - Better UX)
Share a link with token in URL:
```
http://localhost:5000/access?token=cctv-demo-2025-secret
```
The token will auto-fill and submit automatically! ✨

---

## 📝 How to Change the Token

### Option 1: Environment Variable (Production)

1. Set environment variable:
```bash
export ACCESS_TOKEN="your-super-secret-token-here"
```

2. On hosting platforms:
- **Heroku**: `heroku config:set ACCESS_TOKEN="your-token"`
- **Railway**: Add in environment variables
- **Render**: Add in environment variables

### Option 2: Direct Code Change (Quick)

Edit `app/__init__.py` line 18:
```python
app.config['ACCESS_TOKEN'] = 'YOUR-NEW-SECRET-TOKEN-HERE'
```

---

## 💡 Generate Strong Token

Run this command to generate a secure token:
```bash
python -c "import secrets; print('cctv-' + secrets.token_urlsafe(24))"
```

Example output: `cctv-h8K2mP9xL4nQ6wR1tY3sA7dF`

---

## 🚀 Quick Start

1. **Pull latest code:**
```bash
cd ~/camera-website
git pull origin master
```

2. **Run server:**
```bash
python run.py
```

3. **Test access:**
- Visit: `http://localhost:5000`
- Should redirect to `/access` page
- Enter token: `cctv-demo-2025-secret`
- Should redirect to homepage and stay logged in

4. **Share with clients:**
```
http://localhost:5000/access?token=cctv-demo-2025-secret
```

---

## 🎨 Features

✅ Token stored in secure server-side session
✅ Session expires after 30 days
✅ Password field (hidden input)
✅ Auto-login if token in URL
✅ Beautiful access page with animations
✅ Failed attempts show error + shake animation
✅ Protects ALL routes (home, admin, calculator, etc.)

---

## 🧪 Testing

### Test 1: No Access
```bash
# Clear browser cookies/session
# Visit: http://localhost:5000
# Expected: Redirect to /access
```

### Test 2: Wrong Token
```bash
# Enter: wrong-token
# Expected: Error message + shake animation
```

### Test 3: Correct Token
```bash
# Enter: cctv-demo-2025-secret
# Expected: Success + redirect to homepage
```

### Test 4: Auto-Login Link
```bash
# Visit: http://localhost:5000/access?token=cctv-demo-2025-secret
# Expected: Auto-fill + auto-submit + redirect
```

### Test 5: Session Persistence
```bash
# After logging in, close browser
# Open again and visit site
# Expected: Should still have access (30 days)
```

---

## 🔒 Security Features

- ✅ Token never exposed in HTML/JavaScript
- ✅ Session-based authentication (server-side)
- ✅ 30-day session expiration
- ✅ Password input field (hidden)
- ✅ All routes protected with `@require_access` decorator
- ✅ No rate limiting needed (simple token validation)

---

## 🎯 Best Practices

1. **Change default token immediately**
2. **Use strong tokens** (24+ random characters)
3. **Share via direct link** (better UX than manual entry)
4. **Use HTTPS in production** (secure token transmission)
5. **Don't share token publicly** (social media, forums, etc.)
6. **Rotate tokens periodically** for security

---

## 📊 Access Flow Diagram

```
User Request
    |
    v
Has valid session? ──No──> Redirect to /access
    |                              |
   Yes                             v
    |                        Enter token
    v                              |
 Show Page <─────Yes─── Token correct?
                                   |
                                  No
                                   |
                                   v
                            Show error message
```

---

## ❓ FAQ

**Q: Can I have multiple tokens for different clients?**
A: Not by default. You'd need to modify the code to check against a list of tokens.

**Q: How do I revoke access?**
A: Change the token in config. All users will need the new token.

**Q: Can I track who accessed the site?**
A: Add logging in the `validate_access()` function in `routes.py`.

**Q: Is this production-ready?**
A: For demo/preview purposes: YES. For sensitive data: Consider proper authentication (login/password).

**Q: What if user clears cookies?**
A: They'll need to enter token again.

---

## 🔓 Removing Protection Later

If you want to make the site public:

1. Edit `app/routes.py`
2. Remove `@require_access` decorator from routes
3. Delete `/access` and `/validate-access` routes
4. Remove access page template

---

## 📱 Mobile Friendly

✅ Responsive design
✅ Touch-optimized
✅ Works on all devices
✅ Auto-fills token from URL on mobile

---

## 🎉 Summary

**Your CCTV Pro website is now private!**

- ✅ Token: `cctv-demo-2025-secret`
- ✅ Share link: `http://localhost:5000/access?token=cctv-demo-2025-secret`
- ✅ Session duration: 30 days
- ✅ All routes protected

**Next Steps:**
1. Test with default token
2. Change to your own secret token
3. Share access link with clients
4. Deploy to production with HTTPS

---

**Version:** v0.2.1
**Protection:** ✅ Active
**Type:** Token-based access control
**Updated:** December 28, 2025
