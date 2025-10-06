"""Pydantic schemas for customer profile management."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator


class CustomerProfileCreate(BaseModel):
    """Schema for creating a customer profile."""
    first_name: str
    last_name: str
    age: int
    gender: str
    nationality: str
    emirate: str
    city: Optional[str] = None
    employment_status: str
    industry: Optional[str] = None
    position: Optional[str] = None
    monthly_income: str
    household_size: int
    children: str = "No"
    phone_number: Optional[str] = None
    preferred_language: str = "en"
    
    @validator('age')
    def validate_age(cls, v):
        if v < 18 or v > 100:
            raise ValueError('Age must be between 18 and 100')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        allowed = ['male', 'female', 'other', 'prefer_not_to_say']
        if v.lower() not in allowed:
            raise ValueError(f'Gender must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @validator('emirate')
    def validate_emirate(cls, v):
        allowed = [
            'abu_dhabi', 'dubai', 'sharjah', 'ajman', 
            'ras_al_khaimah', 'fujairah', 'umm_al_quwain'
        ]
        if v.lower() not in allowed:
            raise ValueError(f'Emirate must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @validator('employment_status')
    def validate_employment_status(cls, v):
        allowed = [
            'employed_full_time', 'employed_part_time', 'self_employed',
            'unemployed', 'student', 'retired', 'homemaker'
        ]
        if v.lower() not in allowed:
            raise ValueError(f'Employment status must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @validator('monthly_income')
    def validate_monthly_income(cls, v):
        allowed = [
            'below_5000', '5000_10000', '10000_15000', '15000_25000',
            '25000_35000', '35000_50000', '50000_75000', 'above_75000'
        ]
        if v.lower() not in allowed:
            raise ValueError(f'Monthly income must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @validator('household_size')
    def validate_household_size(cls, v):
        if v < 1 or v > 20:
            raise ValueError('Household size must be between 1 and 20')
        return v
    
    @validator('children')
    def validate_children(cls, v):
        allowed = ['yes', 'no']
        if v.lower() not in allowed:
            raise ValueError(f'Children must be one of: {", ".join(allowed)}')
        return v.capitalize()  # Return "Yes" or "No"
    
    @validator('preferred_language')
    def validate_language(cls, v):
        allowed = ['en', 'ar']
        if v.lower() not in allowed:
            raise ValueError(f'Language must be one of: {", ".join(allowed)}')
        return v.lower()


class CustomerProfileUpdate(BaseModel):
    """Schema for updating a customer profile."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    emirate: Optional[str] = None
    city: Optional[str] = None
    employment_status: Optional[str] = None
    industry: Optional[str] = None
    position: Optional[str] = None
    monthly_income: Optional[str] = None
    household_size: Optional[int] = None
    children: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_language: Optional[str] = None
    
    # Apply same validators as create schema
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 18 or v > 100):
            raise ValueError('Age must be between 18 and 100')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v is not None:
            allowed = ['male', 'female', 'other', 'prefer_not_to_say']
            if v.lower() not in allowed:
                raise ValueError(f'Gender must be one of: {", ".join(allowed)}')
            return v.lower()
        return v
    
    @validator('emirate')
    def validate_emirate(cls, v):
        if v is not None:
            allowed = [
                'abu_dhabi', 'dubai', 'sharjah', 'ajman', 
                'ras_al_khaimah', 'fujairah', 'umm_al_quwain'
            ]
            if v.lower() not in allowed:
                raise ValueError(f'Emirate must be one of: {", ".join(allowed)}')
            return v.lower()
        return v
    
    @validator('employment_status')
    def validate_employment_status(cls, v):
        if v is not None:
            allowed = [
                'employed_full_time', 'employed_part_time', 'self_employed',
                'unemployed', 'student', 'retired', 'homemaker'
            ]
            if v.lower() not in allowed:
                raise ValueError(f'Employment status must be one of: {", ".join(allowed)}')
            return v.lower()
        return v
    
    @validator('monthly_income')
    def validate_monthly_income(cls, v):
        if v is not None:
            allowed = [
                'below_5000', '5000_10000', '10000_15000', '15000_25000',
                '25000_35000', '35000_50000', '50000_75000', 'above_75000'
            ]
            if v.lower() not in allowed:
                raise ValueError(f'Monthly income must be one of: {", ".join(allowed)}')
            return v.lower()
        return v
    
    @validator('household_size')
    def validate_household_size(cls, v):
        if v is not None and (v < 1 or v > 20):
            raise ValueError('Household size must be between 1 and 20')
        return v
    
    @validator('children')
    def validate_children(cls, v):
        if v is not None:
            allowed = ['yes', 'no']
            if v.lower() not in allowed:
                raise ValueError(f'Children must be one of: {", ".join(allowed)}')
            return v.capitalize()  # Return "Yes" or "No"
        return v
    
    @validator('preferred_language')
    def validate_language(cls, v):
        if v is not None:
            allowed = ['en', 'ar']
            if v.lower() not in allowed:
                raise ValueError(f'Language must be one of: {", ".join(allowed)}')
            return v.lower()
        return v


class CustomerProfileResponse(BaseModel):
    """Schema for customer profile in responses."""
    id: int
    user_id: int
    first_name: str
    last_name: str
    age: int
    gender: str
    nationality: str
    emirate: str
    city: Optional[str]
    employment_status: str
    industry: Optional[str]
    position: Optional[str]
    monthly_income: str
    household_size: int
    children: str
    phone_number: Optional[str]
    preferred_language: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
