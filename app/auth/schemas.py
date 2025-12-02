"""Pydantic schemas for authentication endpoints."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    username: str
    password: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with _ and - allowed)')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class ChangePassword(BaseModel):
    """Schema for password change by authenticated user."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class SimpleAuthRequest(BaseModel):
    """Schema for simple authentication using email and date of birth."""
    email: EmailStr
    dateOfBirth: str  # ISO date string (YYYY-MM-DD)
    
    @validator('dateOfBirth')
    def validate_date_of_birth(cls, v):
        try:
            from datetime import datetime
            dob = datetime.fromisoformat(v)
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if dob > today:
                raise ValueError('Date of birth cannot be in the future')
            if age < 16 or age > 120:
                raise ValueError('Invalid date of birth')
            
            return v
        except ValueError as e:
            if 'Invalid isoformat string' in str(e):
                raise ValueError('Date must be in YYYY-MM-DD format')
            raise e


class SimpleAuthResponse(BaseModel):
    """Schema for simple authentication response."""
    user_id: int
    email: str
    session_id: str
    survey_history: list
    expires_at: datetime


class PostRegistrationRequest(BaseModel):
    """Schema for post-survey registration request."""
    email: EmailStr
    dateOfBirth: str  # ISO date string (YYYY-MM-DD)
    guestSurveyData: dict  # Survey data from localStorage
    subscribeToUpdates: bool = False
    
    @validator('dateOfBirth')
    def validate_date_of_birth(cls, v):
        try:
            from datetime import datetime
            dob = datetime.fromisoformat(v)
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if dob > today:
                raise ValueError('Date of birth cannot be in the future')
            if age < 16 or age > 120:
                raise ValueError('Invalid date of birth')
            
            return v
        except ValueError as e:
            if 'Invalid isoformat string' in str(e):
                raise ValueError('Date must be in YYYY-MM-DD format')
            raise e
    
    @validator('guestSurveyData')
    def validate_guest_survey_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Guest survey data must be a valid object')
        
        # Check for required fields
        if 'totalScore' not in v:
            raise ValueError('Survey data must include totalScore')
        
        if 'responses' not in v or not isinstance(v['responses'], list):
            raise ValueError('Survey data must include responses array')
        
        return v


class OTPVerifyResponse(BaseModel):
    """Schema for OTP verification response."""
    message: str
    user: dict
    session: dict


class OTPVerifyRequest(BaseModel):
    """Schema for OTP verification request."""
    email: EmailStr
    code: str
    survey_response_id: Optional[int] = None
    profile: Optional[dict] = None


class OTPRequest(BaseModel):
    """Schema for OTP request."""
    email: EmailStr
    language: str = "en"
