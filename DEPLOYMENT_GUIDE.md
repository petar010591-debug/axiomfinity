# FinNews - Railway Deployment Guide

## Prerequisites

Before you start, make sure you have:
- A [Railway](https://railway.app) account (sign up with GitHub)
- Your code pushed to GitHub (use "Save to GitHub" in Emergent)
- A [Cloudinary](https://cloudinary.com) account (free tier is fine)
- Your custom domain ready

---

## Step 1: Get Your Cloudinary Credentials

1. Go to [cloudinary.com](https://cloudinary.com) and sign up (free)
2. From your **Dashboard**, copy these three values:
   - **Cloud Name** (e.g., `dxyz1234`)
   - **API Key** (e.g., `123456789012345`)
   - **API Secret** (e.g., `abcDEF123-ghiJKL456`)

You'll need these in Step 3.

---

## Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app) and click **"New Project"**
2. Choose **"Deploy from GitHub repo"**
3. Select your FinNews repository

Railway will detect the monorepo. You'll create **3 services**: Backend, Frontend, and MongoDB.

---

## Step 3: Add MongoDB

1. In your Railway project, click **"+ New"** → **"Database"** → **"MongoDB"**
2. Railway provisions a MongoDB instance automatically
3. Click on the MongoDB service → **"Variables"** tab
4. Copy the `MONGO_URL` value (looks like `mongodb://mongo:password@hostname:port`)

---

## Step 4: Deploy the Backend

1. Click **"+ New"** → **"GitHub Repo"** → select your repo
2. Go to **Settings** tab:
   - **Root Directory**: `backend`
   - **Builder**: Dockerfile (it will auto-detect `/backend/Dockerfile`)
3. Go to **Variables** tab and add:

```
MONGO_URL=<paste from Step 3>
DB_NAME=finnews
JWT_SECRET=<generate a random 64-char string>
ADMIN_EMAIL=<your admin email>
ADMIN_PASSWORD=<your admin password>
CLOUDINARY_CLOUD_NAME=<from Step 1>
CLOUDINARY_API_KEY=<from Step 1>
CLOUDINARY_API_SECRET=<from Step 1>
SITE_URL=https://yourdomain.com
```

> To generate JWT_SECRET, run in terminal: `openssl rand -hex 32`

4. Go to **Settings** → **Networking** → **Generate Domain** (gives you a Railway URL like `backend-xxx.up.railway.app`)
5. Note this URL — you need it for the frontend

---

## Step 5: Deploy the Frontend

1. Click **"+ New"** → **"GitHub Repo"** → select your repo again
2. Go to **Settings** tab:
   - **Root Directory**: `frontend`
   - **Builder**: Dockerfile
3. Go to **Variables** tab and add:

```
REACT_APP_BACKEND_URL=https://<backend-railway-url-from-step-4>
```

> **Important**: This is a build-time variable. The Dockerfile uses `ARG` to bake it into the React build.

4. Go to **Settings** → **Networking** → **Generate Domain**

---

## Step 6: Configure Backend CORS (if needed)

Your backend already allows all origins (`allow_origins=["*"]`). For production, you may want to restrict this to your domain. Edit `server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 7: Connect Your Custom Domain

### For the Frontend (your main domain):

1. In Railway, click on your **Frontend service**
2. Go to **Settings** → **Networking** → **Custom Domain**
3. Click **"+ Custom Domain"**
4. Enter your domain: `yourdomain.com`
5. Railway shows you DNS records to add. Go to your domain registrar and add:

   | Type  | Name | Value                          |
   |-------|------|--------------------------------|
   | CNAME | @    | `<railway-provided-value>.up.railway.app` |

   If your registrar doesn't support CNAME on root (`@`), add:
   
   | Type  | Name | Value                          |
   |-------|------|--------------------------------|
   | CNAME | www  | `<railway-provided-value>.up.railway.app` |

   Then set up a redirect from `yourdomain.com` → `www.yourdomain.com` at your registrar.

6. Wait for DNS propagation (usually 5-30 minutes)
7. Railway auto-provisions SSL certificate once DNS is verified

### For the Backend API (subdomain):

1. Click on your **Backend service**
2. Go to **Settings** → **Networking** → **Custom Domain**
3. Add: `api.yourdomain.com`
4. At your registrar, add:

   | Type  | Name | Value                          |
   |-------|------|--------------------------------|
   | CNAME | api  | `<railway-provided-value>.up.railway.app` |

5. After DNS propagates, update your **Frontend** service's variable:
   ```
   REACT_APP_BACKEND_URL=https://api.yourdomain.com
   ```
6. Redeploy the frontend (Railway does this automatically on variable change)

---

## Step 8: Verify Everything Works

1. Visit `https://yourdomain.com` — homepage should load with ticker + articles
2. Visit `https://yourdomain.com/admin/login` — log in with your admin credentials
3. Create a test article with an image upload — confirms Cloudinary works
4. Visit `https://api.yourdomain.com/api/sitemap.xml` — should show XML sitemap

---

## Architecture After Deployment

```
yourdomain.com (Frontend - Nginx serving React build)
    |
    v
api.yourdomain.com (Backend - FastAPI on Railway)
    |
    +---> MongoDB (Railway internal database)
    +---> Cloudinary (Image storage CDN)
    +---> CoinGecko API (Market data)
```

---

## Environment Variables Reference

### Backend
| Variable               | Required | Description                          |
|------------------------|----------|--------------------------------------|
| MONGO_URL              | Yes      | MongoDB connection string            |
| DB_NAME                | Yes      | Database name (use `finnews`)        |
| JWT_SECRET             | Yes      | Random secret for token signing      |
| ADMIN_EMAIL            | Yes      | Default admin account email          |
| ADMIN_PASSWORD         | Yes      | Default admin account password       |
| CLOUDINARY_CLOUD_NAME  | Yes      | Cloudinary cloud name                |
| CLOUDINARY_API_KEY     | Yes      | Cloudinary API key                   |
| CLOUDINARY_API_SECRET  | Yes      | Cloudinary API secret                |
| SITE_URL               | No       | Public URL for sitemap generation    |

### Frontend
| Variable                | Required | Description                        |
|-------------------------|----------|------------------------------------|
| REACT_APP_BACKEND_URL   | Yes      | Backend API URL (build-time)       |

---

## Troubleshooting

**Frontend shows blank page**: Check that `REACT_APP_BACKEND_URL` was set BEFORE the build. It's a build-time variable — changing it requires a redeploy.

**API returns CORS errors**: Verify the backend's `allow_origins` includes your frontend domain.

**Images fail to upload**: Check Cloudinary credentials in backend variables. Look at Railway logs for the backend service.

**Market ticker shows stale prices**: CoinGecko free tier has rate limits. Prices cache for 2 minutes. For higher limits, add a CoinGecko API key.

**Database connection fails**: Verify `MONGO_URL` in backend variables matches the Railway MongoDB service's connection string. Use the **Reference Variable** feature: `${{MongoDB.MONGO_URL}}`.

---

## Cost Estimate (Railway)

- **Hobby Plan**: $5/month (includes $5 credit)
  - Covers small-medium traffic for all 3 services
- **MongoDB**: Included in Railway (or use free MongoDB Atlas for more control)
- **Cloudinary**: Free tier = 25GB storage, 25GB bandwidth/month
- **Custom Domain + SSL**: Free (Railway handles this automatically)
