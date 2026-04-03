# FinNews - Railway Deployment Guide

## Prerequisites

- A [Railway](https://railway.app) account (sign up with GitHub)
- Your code pushed to GitHub (use "Save to GitHub" in Emergent)
- A [Cloudinary](https://cloudinary.com) account (free tier is fine)

---

## Step 1: Get Your Cloudinary Credentials

1. Go to [cloudinary.com](https://cloudinary.com) and sign up (free)
2. From your **Dashboard**, copy:
   - **Cloud Name** (e.g., `dxyz1234`)
   - **API Key** (e.g., `123456789012345`)
   - **API Secret** (e.g., `abcDEF123-ghiJKL456`)

---

## Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app) → **"New Project"**
2. Choose **"Deploy from GitHub repo"** → select your FinNews repository

You will create **3 services**: MongoDB, Backend, and Frontend.

---

## Step 3: Add MongoDB

1. In your Railway project, click **"+ New"** → **"Database"** → **"MongoDB"**
2. Railway auto-provisions MongoDB
3. Note: You'll reference this as `${{MongoDB.MONGO_URL}}` in the backend variables

---

## Step 4: Deploy the Backend

1. Click **"+ New"** → **"GitHub Repo"** → select your repo
2. **Settings** tab:
   - **Root Directory**: `backend`
   - **Builder**: Dockerfile (auto-detected)
3. **Networking** tab:
   - Click **"Generate Domain"** → gives you something like `backend-abc123.up.railway.app`
   - **COPY THIS URL** — you need it for Step 5
4. **Variables** tab — add ALL of these:

```
MONGO_URL=${{MongoDB.MONGO_URL}}
DB_NAME=finnews
JWT_SECRET=<run: openssl rand -hex 32>
ADMIN_EMAIL=petar010591@gmail.com
ADMIN_PASSWORD=Zvezda2023!
CLOUDINARY_CLOUD_NAME=<from Step 1>
CLOUDINARY_API_KEY=<from Step 1>
CLOUDINARY_API_SECRET=<from Step 1>
SITE_URL=https://yourdomain.com
PORT=8001
```

> **Important**: `${{MongoDB.MONGO_URL}}` is a Railway reference variable — type it exactly like that and Railway auto-fills the real connection string.

---

## Step 5: Deploy the Frontend

1. Click **"+ New"** → **"GitHub Repo"** → select your repo again
2. **Settings** tab:
   - **Root Directory**: `frontend`
   - **Builder**: Dockerfile (auto-detected)
3. **Variables** tab — add:

```
BACKEND_URL=https://<backend-domain-from-step-4>
```

For example: `BACKEND_URL=https://backend-abc123.up.railway.app`

> **How this works**: The frontend nginx server proxies all `/api` requests to your backend service. No CORS issues, clean URLs.

4. **Networking** tab → **Generate Domain** (this is your public site URL)

---

## Step 6: Verify It Works

1. Visit your **frontend URL** → homepage should show with ticker + articles
2. Go to `/admin/login` → log in with `petar010591@gmail.com` / `Zvezda2023!`
3. Check the backend logs in Railway if something doesn't work

---

## Step 7: Connect Your Custom Domain

### Frontend (main domain):

1. In Railway → **Frontend service** → **Settings** → **Networking** → **Custom Domain**
2. Click **"+ Custom Domain"** → enter `yourdomain.com`
3. Railway shows DNS records. At your domain registrar, add:

   | Type  | Name | Value |
   |-------|------|-------|
   | CNAME | www  | `<railway-value>.up.railway.app` |

   For root domain (`@`), if your registrar supports it:
   | Type  | Name | Value |
   |-------|------|-------|
   | CNAME | @    | `<railway-value>.up.railway.app` |

4. Wait 5-30 minutes for DNS propagation
5. Railway auto-provisions SSL

### After domain is connected:

Update `SITE_URL` in backend variables to your real domain (for sitemap generation):
```
SITE_URL=https://yourdomain.com
```

---

## Architecture on Railway

```
yourdomain.com
      |
      v
  [Frontend Service - Nginx]
      |
      |  /api/* requests proxied to:
      v
  [Backend Service - FastAPI]
      |
      v
  [MongoDB Service]
      |
  [Cloudinary CDN - images]
  [CoinGecko API - market data]
```

**Key point**: Only the frontend needs a public domain. The backend communicates through the frontend's nginx proxy. This means:
- No CORS issues
- Single domain for everything
- Backend stays private

---

## Environment Variables Reference

### Backend Service
| Variable               | Required | Example                          |
|------------------------|----------|----------------------------------|
| MONGO_URL              | Yes      | `${{MongoDB.MONGO_URL}}`         |
| DB_NAME                | Yes      | `finnews`                        |
| JWT_SECRET             | Yes      | `a1b2c3...` (64 random chars)    |
| ADMIN_EMAIL            | Yes      | `petar010591@gmail.com`          |
| ADMIN_PASSWORD         | Yes      | `Zvezda2023!`                    |
| CLOUDINARY_CLOUD_NAME  | Yes      | `dxyz1234`                       |
| CLOUDINARY_API_KEY     | Yes      | `123456789012345`                |
| CLOUDINARY_API_SECRET  | Yes      | `abcDEF123-ghiJKL456`           |
| SITE_URL               | No       | `https://yourdomain.com`         |
| PORT                   | No       | `8001` (Railway auto-sets this)  |

### Frontend Service
| Variable     | Required | Example                                        |
|--------------|----------|-------------------------------------------------|
| BACKEND_URL  | Yes      | `https://backend-abc123.up.railway.app`         |

---

## Troubleshooting

**Login returns 405 error**: `BACKEND_URL` is not set on the frontend service. Nginx can't proxy to backend.

**Login says "Invalid email or password"**: Check that `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set in backend variables. Redeploy the backend — it resets the admin password on every startup.

**Frontend shows blank page**: Check Railway logs for the frontend service. The build might have failed.

**Images fail to upload**: Verify all 3 Cloudinary variables are set in backend.

**Market ticker shows stale prices**: Normal — CoinGecko free tier has rate limits. Prices cache for 2 minutes.

**MongoDB "Attempting to connect..."**: Railway's built-in DB viewer can be slow. If the backend connects fine (check backend logs), the DB is working.

---

## Cost

- **Railway Hobby Plan**: $5/month (includes $5 usage credit)
- **Cloudinary**: Free (25GB storage, 25GB bandwidth)
- **Custom Domain + SSL**: Free (Railway handles this)
