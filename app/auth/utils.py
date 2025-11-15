"""Authentication utilities and JWT token management."""
from datetime import datetime, timedelta
from typing import Optional, Union
import bcrypt
from jose import JWTError, jwt
from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash using direct bcrypt."""
    try:
        # Convert strings to bytes
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        
        # Use bcrypt directly to avoid passlib issues
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using direct bcrypt."""
    try:
        # Ensure password is within bcrypt limits (72 bytes)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError("Password too long for bcrypt (max 72 bytes)")
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, is_admin: bool = False) -> str:
    """Create a JWT access token with role-based expiration."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Use longer expiration for admin users
        expire_minutes = settings.ADMIN_TOKEN_EXPIRE_MINUTES if is_admin else settings.ACCESS_TOKEN_EXPIRE_MINUTES
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_admin_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token specifically for admin users with longer expiration."""
    return create_access_token(data, expires_delta, is_admin=True)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with longer expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_simple_session(user_id: int) -> tuple[str, datetime]:
    """Create a simple session ID and expiration time."""
    import secrets
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hour session
    return session_id, expires_at


def verify_simple_session(session_id: str, db) -> Optional[int]:
    """Verify a simple session and return user_id if valid."""
    from app.models import SimpleSession
    
    session = db.query(SimpleSession).filter(
        SimpleSession.session_id == session_id,
        SimpleSession.is_active == True,
        SimpleSession.expires_at > datetime.utcnow()
    ).first()
    
    return session.user_id if session else None
