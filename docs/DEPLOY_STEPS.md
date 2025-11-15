# Quick Heroku Deployment Steps

## 1. Login to Heroku
```bash
heroku login
```
This will open your browser for authentication.

## 2. Run the deployment script
```bash
cd backend
./deploy-manual.sh
```

## 3. Alternative: Manual commands

If the script doesn't work, run these commands one by one:

```bash
# Create app
heroku create uae-financial-health-api --region us

# Add database
heroku addons:create heroku-postgresql:essential-0 --app uae-financial-health-api

# Set environment variables
heroku config:set ENVIRONMENT=production --app uae-financial-health-api
heroku config:set DEBUG=false --app uae-financial-health-api
heroku config:set SECRET_KEY=$(openssl rand -base64 32) --app uae-financial-health-api

# Deploy
git init  # if not already a git repo
git add .
git commit -m "Initial deployment"
heroku git:remote -a uae-financial-health-api
git push heroku main

# Run migrations
heroku run python -m alembic upgrade head --app uae-financial-health-api
```

## 4. Test your API

Your API will be available at: `https://uae-financial-health-api.herokuapp.com`

Test endpoints:
- Health check: `GET /health`
- API docs: `GET /docs` (only in development)
- Root: `GET /`

## 5. Monitor

```bash
# View logs
heroku logs --tail --app uae-financial-health-api

# Check status
heroku ps --app uae-financial-health-api

# Open in browser
heroku open --app uae-financial-health-api
```

## Cost

- PostgreSQL Essential-0: $5/month
- Eco dyno: $5/month
- **Total: ~$10/month**

## Troubleshooting

If deployment fails:
1. Check logs: `heroku logs --tail`
2. Ensure all files are committed to git
3. Check that requirements.txt includes all dependencies
4. Verify Procfile is correct