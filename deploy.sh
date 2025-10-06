#!/bin/bash

# Heroku Deployment Script for UAE Financial Health Check Backend

echo "🚀 Deploying to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Login to Heroku (if not already logged in)
echo "🔐 Checking Heroku authentication..."
heroku auth:whoami || heroku login

# Create Heroku app (if it doesn't exist)
APP_NAME="uae-financial-health-api"
echo "📱 Creating Heroku app: $APP_NAME"
heroku create $APP_NAME --region us || echo "App might already exist, continuing..."

# Add PostgreSQL addon
echo "🗄️ Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:essential-0 --app $APP_NAME || echo "Database might already exist, continuing..."

# Set environment variables
echo "⚙️ Setting environment variables..."
heroku config:set ENVIRONMENT=production --app $APP_NAME
heroku config:set DEBUG=false --app $APP_NAME
heroku config:set SECRET_KEY=$(openssl rand -base64 32) --app $APP_NAME
heroku config:set ALGORITHM=HS256 --app $APP_NAME
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30 --app $APP_NAME
heroku config:set REFRESH_TOKEN_EXPIRE_DAYS=7 --app $APP_NAME

# Deploy to Heroku
echo "🚀 Deploying application..."
git add .
git commit -m "Deploy to Heroku" || echo "No changes to commit"
heroku git:remote -a $APP_NAME
git push heroku main || git push heroku master

# Run database migrations
echo "🔄 Running database migrations..."
heroku run python -m alembic upgrade head --app $APP_NAME

# Open the app
echo "✅ Deployment complete!"
echo "🌐 Opening app in browser..."
heroku open --app $APP_NAME

echo "📊 App info:"
heroku info --app $APP_NAME