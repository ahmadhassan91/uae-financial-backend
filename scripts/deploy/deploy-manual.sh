#!/bin/bash

# Manual Heroku Deployment Script
# Run this after logging in with: heroku login

set -e

APP_NAME="uae-financial-health-api"
echo "🚀 Deploying UAE Financial Health Check API to Heroku..."

# Check if logged in
echo "🔐 Checking Heroku authentication..."
if ! heroku auth:whoami; then
    echo "❌ Please login first with: heroku login"
    exit 1
fi

# Create app if it doesn't exist
echo "📱 Creating/checking Heroku app: $APP_NAME"
if ! heroku apps:info $APP_NAME >/dev/null 2>&1; then
    echo "Creating new app..."
    heroku create $APP_NAME --region us
else
    echo "App already exists, continuing..."
fi

# Add PostgreSQL addon (essential-0 is the cheapest paid plan)
echo "🗄️ Adding PostgreSQL database..."
if ! heroku addons:info postgresql --app $APP_NAME >/dev/null 2>&1; then
    echo "Adding PostgreSQL addon..."
    heroku addons:create heroku-postgresql:essential-0 --app $APP_NAME
else
    echo "PostgreSQL addon already exists, continuing..."
fi

# Set environment variables
echo "⚙️ Setting environment variables..."
heroku config:set \
    ENVIRONMENT=production \
    DEBUG=false \
    SECRET_KEY=$(openssl rand -base64 32) \
    ALGORITHM=HS256 \
    ACCESS_TOKEN_EXPIRE_MINUTES=30 \
    REFRESH_TOKEN_EXPIRE_DAYS=7 \
    --app $APP_NAME

# Initialize git if not already done
if [ ! -d .git ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
fi

# Add Heroku remote
echo "🔗 Adding Heroku remote..."
heroku git:remote -a $APP_NAME

# Deploy
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku $(date)" || echo "No changes to commit"
git push heroku HEAD:main

# Run migrations
echo "🔄 Running database migrations..."
heroku run python -m alembic upgrade head --app $APP_NAME

# Show app info
echo "✅ Deployment complete!"
echo ""
echo "📊 App Information:"
heroku info --app $APP_NAME
echo ""
echo "🌐 Your API is available at:"
heroku apps:info $APP_NAME --json | grep web_url | cut -d'"' -f4
echo ""
echo "📋 Useful commands:"
echo "  View logs: heroku logs --tail --app $APP_NAME"
echo "  Open app: heroku open --app $APP_NAME"
echo "  Check status: heroku ps --app $APP_NAME"