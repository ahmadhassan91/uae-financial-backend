"""Authentication routes for user registration, login, and token management."""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, AuditLog, SimpleSession
from app.auth.schemas import (
    UserCreate, UserLogin, UserResponse, Token, 
    RefreshTokenRequest, ChangePassword, SimpleAuthRequest, SimpleAuthResponse,
    PostRegistrationRequest
)
from app.auth.utils import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token, create_simple_session
)
from app.auth.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log registration
    audit_log = AuditLog(
        user_id=db_user.id,
        action="user_registered",
        entity_type="user",
        entity_id=db_user.id,
        details={"email": db_user.email, "username": db_user.username}
    )
    db.add(audit_log)
    db.commit()
    
    return db_user


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """Authenticate user and return JWT tokens."""
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    # Log login
    audit_log = AuditLog(
        user_id=user.id,
        action="user_login",
        entity_type="user",
        entity_id=user.id,
        details={"email": user.email}
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token."""
    # Verify refresh token
    payload = verify_token(token_data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if user exists and is active
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information."""
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Change user password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    # Log password change
    audit_log = AuditLog(
        user_id=current_user.id,
        action="password_changed",
        entity_type="user",
        entity_id=current_user.id,
        details={"email": current_user.email}
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Logout user (for audit trail purposes)."""
    # Log logout
    audit_log = AuditLog(
        user_id=current_user.id,
        action="user_logout",
        entity_type="user",
        entity_id=current_user.id,
        details={"email": current_user.email}
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Logged out successfully"}


@router.post("/simple-login", response_model=SimpleAuthResponse)
async def simple_login(
    auth_data: SimpleAuthRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Simple authentication using email and date of birth."""
    from datetime import datetime
    
    # Simple rate limiting - check for recent failed attempts
    recent_attempts = db.query(AuditLog).filter(
        AuditLog.action == "simple_login_failed",
        AuditLog.details.op('->>')('email') == auth_data.email,
        AuditLog.created_at > datetime.utcnow() - timedelta(minutes=15)
    ).count()
    
    if recent_attempts >= 20:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please try again later."
        )
    
    # Parse date of birth
    try:
        dob = datetime.fromisoformat(auth_data.dateOfBirth)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Find user by email
    user = db.query(User).filter(User.email == auth_data.email).first()
    
    if not user:
        # Log failed attempt
        audit_log = AuditLog(
            action="simple_login_failed",
            entity_type="user",
            details={"email": auth_data.email, "reason": "user_not_found"}
        )
        db.add(audit_log)
        db.commit()
        
        # For security, don't reveal whether email exists
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or date of birth"
        )
    
    # Check if user has date of birth set
    if user.date_of_birth is None:
        # First time using simple auth - set the date of birth
        user.date_of_birth = dob.date()
        db.commit()
    else:
        # Compare dates properly (handle both date and datetime objects)
        user_dob = user.date_of_birth
        if hasattr(user_dob, 'date'):
            user_dob = user_dob.date()
        
        if user_dob != dob.date():
            # Log failed attempt
            audit_log = AuditLog(
                user_id=user.id,
                action="simple_login_failed",
                entity_type="user",
                entity_id=user.id,
                details={"email": user.email, "reason": "date_mismatch"}
            )
            db.add(audit_log)
            db.commit()
            
            # Date of birth doesn't match
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or date of birth"
            )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create simple session
    session_id, expires_at = create_simple_session(user.id)
    
    # Store session in database
    simple_session = SimpleSession(
        user_id=user.id,
        session_id=session_id,
        expires_at=expires_at
    )
    db.add(simple_session)
    
    # Get user's survey history
    from app.models import SurveyResponse
    survey_responses = db.query(SurveyResponse).filter(
        SurveyResponse.user_id == user.id
    ).order_by(SurveyResponse.created_at.desc()).limit(50).all()
    
    survey_history = []
    for response in survey_responses:
        survey_history.append({
            "id": response.id,
            "overall_score": response.overall_score,
            "budgeting_score": response.budgeting_score,
            "savings_score": response.savings_score,
            "debt_management_score": response.debt_management_score,
            "financial_planning_score": response.financial_planning_score,
            "investment_knowledge_score": response.investment_knowledge_score,
            "risk_tolerance": response.risk_tolerance,
            "created_at": response.created_at.isoformat(),
            "completion_time": response.completion_time
        })
    
    # Log simple login
    audit_log = AuditLog(
        user_id=user.id,
        action="simple_login",
        entity_type="user",
        entity_id=user.id,
        details={"email": user.email, "session_id": session_id}
    )
    db.add(audit_log)
    db.commit()
    
    return SimpleAuthResponse(
        user_id=user.id,
        email=user.email,
        session_id=session_id,
        survey_history=survey_history,
        expires_at=expires_at
    )


@router.post("/post-register", response_model=SimpleAuthResponse)
async def post_survey_registration(
    registration_data: PostRegistrationRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Register a guest user after completing a survey and migrate their data."""
    from datetime import datetime
    from app.auth.post_registration import PostRegistrationService
    
    try:
        # Parse date of birth
        dob = datetime.fromisoformat(registration_data.dateOfBirth)
        
        # Create post-registration service
        post_reg_service = PostRegistrationService(db)
        
        # Register user and migrate data
        result = await post_reg_service.register_guest_user(
            email=registration_data.email,
            date_of_birth=dob,
            guest_survey_data=registration_data.guestSurveyData,
            subscribe_to_updates=registration_data.subscribeToUpdates
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Post-registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )
