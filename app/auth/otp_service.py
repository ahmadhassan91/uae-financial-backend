"""OTP Service for email verification and authentication."""
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import OTPCode, User
from app.auth.account_lockout import AccountLockoutService

logger = logging.getLogger(__name__)


class OTPService:
    """Service for generating, verifying, and managing OTP codes."""
    
    # Configuration
    OTP_EXPIRATION_MINUTES = 5
    OTP_MAX_ATTEMPTS = 3
    RATE_LIMIT_MINUTES = 15
    RATE_LIMIT_MAX_OTPS = 5  # Maximum 5 OTP requests per 15 minutes
    
    @staticmethod
    def generate_otp(email: str, db: Session) -> Dict[str, Any]:
        """
        Generate a 6-digit OTP and store in database.
        
        Args:
            email: User's email address
            db: Database session
            
        Returns:
            Dict with success status, code (if successful), and message
        """
        # Rate limiting: Check recent OTPs
        recent_cutoff = datetime.utcnow() - timedelta(minutes=OTPService.RATE_LIMIT_MINUTES)
        recent_count = db.query(OTPCode).filter(
            and_(
                OTPCode.email == email,
                OTPCode.created_at > recent_cutoff
            )
        ).count()
        
        if recent_count >= OTPService.RATE_LIMIT_MAX_OTPS:
            return {
                'success': False,
                'message': f'Too many OTP requests. Please try again in {OTPService.RATE_LIMIT_MINUTES} minutes.',
                'code': None
            }
        
        # Generate secure 6-digit code
        code = str(secrets.randbelow(1000000)).zfill(6)
        expires_at = datetime.utcnow() + timedelta(minutes=OTPService.OTP_EXPIRATION_MINUTES)
        
        # Store in database
        otp = OTPCode(
            email=email,
            code=code,
            expires_at=expires_at,
            attempt_count=0,
            is_used=False
        )
        db.add(otp)
        db.commit()
        db.refresh(otp)
        
        return {
            'success': True,
            'code': code,
            'expires_in': OTPService.OTP_EXPIRATION_MINUTES * 60,  # seconds
            'message': 'OTP generated successfully'
        }
    
    @staticmethod
    def verify_otp(
        email: str, 
        code: str, 
        db: Session,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify OTP code with account lockout protection.
        
        Args:
            email: User's email address
            code: 6-digit OTP code
            db: Database session
            ip_address: Client IP for lockout tracking
            user_agent: Client user agent for logging
            
        Returns:
            Dict with success status, user info, and message
        """
        # Check if account is locked out
        lockout_check = AccountLockoutService.check_lockout(
            identifier=email,
            identifier_type="email",
            attempt_type="otp_verify",
            db=db
        )
        
        if lockout_check['is_locked']:
            logger.warning(f"OTP verification blocked - Account locked: {email}")
            return {
                'success': False,
                'message': lockout_check['message'],
                'user_exists': False,
                'user_id': None,
                'is_locked': True,
                'remaining_seconds': lockout_check['remaining_seconds']
            }
        
        # Find most recent unused OTP for this email
        otp = db.query(OTPCode).filter(
            and_(
                OTPCode.email == email,
                OTPCode.code == code,
                OTPCode.is_used == False
            )
        ).order_by(OTPCode.created_at.desc()).first()
        
        if not otp:
            # Record failed attempt
            lockout_result = AccountLockoutService.record_failed_attempt(
                identifier=email,
                identifier_type="email",
                attempt_type="otp_verify",
                db=db,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            message = 'Invalid OTP code'
            if lockout_result.get('message'):
                message += f". {lockout_result['message']}"
            
            return {
                'success': False,
                'message': message,
                'user_exists': False,
                'user_id': None,
                'remaining_attempts': lockout_result.get('remaining_attempts'),
                'is_locked': lockout_result.get('is_locked', False)
            }
        
        # Check expiration
        if otp.expires_at < datetime.utcnow():
            return {
                'success': False,
                'message': 'OTP code has expired. Please request a new one.',
                'user_exists': False,
                'user_id': None
            }
        
        # Check attempt count on the OTP itself
        if otp.attempt_count >= OTPService.OTP_MAX_ATTEMPTS:
            return {
                'success': False,
                'message': 'Too many verification attempts. Please request a new OTP.',
                'user_exists': False,
                'user_id': None
            }
        
        # Valid OTP - mark as used and reset lockout counter
        otp.is_used = True
        otp.used_at = datetime.utcnow()
        
        # Reset lockout counter on successful verification
        AccountLockoutService.record_successful_attempt(
            identifier=email,
            identifier_type="email",
            attempt_type="otp_verify",
            db=db
        )
        
        db.commit()
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        logger.info(f"OTP verified successfully for: {email}")
        
        return {
            'success': True,
            'message': 'OTP verified successfully',
            'user_exists': user is not None,
            'user_id': user.id if user else None
        }
    
    @staticmethod
    def increment_attempt(email: str, code: str, db: Session) -> None:
        """Increment attempt count for failed OTP verification."""
        otp = db.query(OTPCode).filter(
            and_(
                OTPCode.email == email,
                OTPCode.code == code,
                OTPCode.is_used == False
            )
        ).order_by(OTPCode.created_at.desc()).first()
        
        if otp:
            otp.attempt_count += 1
            db.commit()
    
    @staticmethod
    def cleanup_expired_otps(db: Session) -> int:
        """
        Delete OTP codes older than 24 hours.
        
        Returns:
            Number of deleted records
        """
        cutoff = datetime.utcnow() - timedelta(hours=24)
        deleted = db.query(OTPCode).filter(
            OTPCode.created_at < cutoff
        ).delete()
        db.commit()
        return deleted
