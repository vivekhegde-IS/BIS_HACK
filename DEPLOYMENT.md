# Instructions for Deploying Backend (Render) and Frontend (Vercel)

## Backend (Render)
1. Make sure your backend (Flask app) is in `src/app.py`.
2. Add a `render.yaml` for Render deployment configuration.
3. Ensure requirements.txt is up to date.
4. Expose the Flask app as `app` in `src/app.py` (Render expects `app` or `application`).

## Frontend (Vercel)
1. Place your static frontend files (e.g., index.html) in the `frontend/` directory.
2. Deploy the `frontend/` directory to Vercel as a static site.
3. Update API URLs in your frontend to point to the Render backend URL after deployment.

---

## Example `render.yaml` for Render

services:
  - type: web
    name: bis-hack-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn -w 1 -b 0.0.0.0:10000 src.app:app"
    plan: free
    envVars:
      - key: PORT
        value: 10000

---

## Example `src/app.py` (entrypoint)

from flask import Flask
app = Flask(__name__)
# ...existing code...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

---

## After Deployment
- Update your frontend (in `frontend/index.html`) to use the Render backend URL for API calls.
