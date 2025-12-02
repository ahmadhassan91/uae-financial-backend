# Heroku Deployment Guide

## Prerequisites

1. **Heroku CLI**: Install from https://devcenter.heroku.com/articles/heroku-cli
2. **Git**: Ensure your project is in a Git repository
3. **Heroku Account**: Sign up at https://heroku.com

## Quick Deployment

### Option 1: Using the deployment script
```bash
cd backend
./deploy.sh
```

### Option 2: Manual deployment

1. **Login to Heroku**
```bash
heroku login
```

2. **Create Heroku app**
```bash
heroku create your-app-name --region us
```

3. **Add PostgreSQL database**
```bash
heroku addons:create heroku-postgresql:essential-0
```

4. **Set environment variables**
```bash
heroku config:set ENVIRONMENT=production
heroku config:set DEBUG=false
heroku config:set SECRET_KEY=$(openssl rand -base64 32)
heroku config:set ALGORITHM=HS256
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30
heroku config:set REFRESH_TOKEN_EXPIRE_DAYS=7
```

5. **Deploy the application**
```bash
# From the backend directory
git add .
git commit -m "Deploy to Heroku"
heroku git:remote -a your-app-name
git push heroku main
```

6. **Run database migrations**
```bash
heroku run python -m alembic upgrade head
```

## Environment Variables

The following environment variables are automatically set:
- `DATABASE_URL`: PostgreSQL connection string (set by Heroku)
- `PORT`: Application port (set by Heroku)

You should set these manually:
- `SECRET_KEY`: JWT secret key
- `ENVIRONMENT`: Set to "production"
- `DEBUG`: Set to "false"

## Database Setup

Heroku automatically provides a PostgreSQL database. The `DATABASE_URL` environment variable is automatically configured.

## Scaling

For basic usage, the free tier should be sufficient:
```bash
heroku ps:scale web=1
```

For production with more traffic:
```bash
heroku ps:scale web=2
```

## Monitoring

- **View logs**: `heroku logs --tail`
- **Check app status**: `heroku ps`
- **Open app**: `heroku open`

## Troubleshooting

### Common Issues

1. **Build fails**: Check that all dependencies are in `requirements.txt`
2. **Database connection fails**: Ensure migrations are run with `heroku run python -m alembic upgrade head`
3. **CORS issues**: Update `ALLOWED_ORIGINS` in config.py to include your frontend domain

### Useful Commands

```bash
# View environment variables
heroku config

# Access database
heroku pg:psql

# Restart app
heroku restart

# View app info
heroku info
```

## Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Set `DEBUG=false`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure CORS for your frontend domain
- [ ] Run database migrations
- [ ] Test all API endpoints
- [ ] Set up monitoring/logging

## Cost Optimization

For minimal cost:
- Use `essential-0` PostgreSQL plan ($5/month)
- Use `eco` dyno type ($5/month)
- Total: ~$10/month for basic production setup

## Security Notes

- Never commit sensitive environment variables to Git
- Use Heroku's config vars for all secrets
- Enable HTTPS (automatic with Heroku)
- Regularly rotate SECRET_KEY and database credentials