"""Customer profile routes for managing user profiles."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, CustomerProfile, AuditLog
from app.customers.schemas import (
    CustomerProfileCreate, CustomerProfileUpdate, CustomerProfileResponse
)
from app.auth.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/customers", tags=["customer-profiles"])


@router.post("/profile", response_model=CustomerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_profile(
    profile_data: CustomerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a customer profile for the current user."""
    # Check if user already has a profile
    existing_profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a customer profile"
        )
    
    # Create new profile
    db_profile = CustomerProfile(
        user_id=current_user.id,
        **profile_data.dict()
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    # Log profile creation
    audit_log = AuditLog(
        user_id=current_user.id,
        action="profile_created",
        entity_type="customer_profile",
        entity_id=db_profile.id,
        details={"profile_id": db_profile.id}
    )
    db.add(audit_log)
    db.commit()
    
    return db_profile


@router.get("/profile", response_model=CustomerProfileResponse)
async def get_customer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get the current user's customer profile."""
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    
    return profile


@router.put("/profile", response_model=CustomerProfileResponse)
async def update_customer_profile(
    profile_data: CustomerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update the current user's customer profile."""
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    
    # Update only provided fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    # Log profile update
    audit_log = AuditLog(
        user_id=current_user.id,
        action="profile_updated",
        entity_type="customer_profile",
        entity_id=profile.id,
        details={"updated_fields": list(update_data.keys())}
    )
    db.add(audit_log)
    db.commit()
    
    return profile


@router.delete("/profile")
async def delete_customer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete the current user's customer profile."""
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    
    # Log profile deletion before removing
    audit_log = AuditLog(
        user_id=current_user.id,
        action="profile_deleted",
        entity_type="customer_profile",
        entity_id=profile.id,
        details={"profile_id": profile.id}
    )
    db.add(audit_log)
    
    # Delete profile
    db.delete(profile)
    db.commit()
    
    return {"message": "Customer profile deleted successfully"}


# Admin routes
@router.get("/profiles", response_model=List[CustomerProfileResponse])
async def list_customer_profiles(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all customer profiles (admin only)."""
    profiles = db.query(CustomerProfile).offset(skip).limit(limit).all()
    return profiles


@router.get("/profiles/{profile_id}", response_model=CustomerProfileResponse)
async def get_customer_profile_by_id(
    profile_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific customer profile by ID (admin only)."""
    profile = db.query(CustomerProfile).filter(CustomerProfile.id == profile_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    
    return profile
