#!/usr/bin/env python3
"""Check if admin user exists."""

from app.database import SessionLocal
from app.models import User

def check_admin():
    """Check if admin user exists."""
    db = SessionLocal()
    
    try:
        admin = db.query(User).filter(User.email == 'admin@nationalbonds.ae').first()
        if admin:
            print('✅ Admin user exists!')
            print('Email: admin@nationalbonds.ae')
            print('🔗 Access admin at: https://uae-financial-health-api-4188fd6ae86c.herokuapp.com/admin')
        else:
            print('❌ No admin user found')
            
        # Also check total users
        total_users = db.query(User).count()
        print(f'📊 Total users in database: {total_users}')
        
    except Exception as e:
        print(f'❌ Error checking admin: {e}')
    finally:
        db.close()

if __name__ == '__main__':
    check_admin()