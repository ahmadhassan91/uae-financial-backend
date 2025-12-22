"""
Account Lockout Service for brute-force protection.

Implements security audit recommendations:
- Track failed login/OTP attempts
- Temporarily lock accounts after repeated failures
- Progressive delays between attempts
- Notify users of suspicious activity
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
import math

from app.models import FailedLoginAttempt, AuditLog

logger = logging.getLogger(__name__)


class AccountLockoutService:
    """Service for managing account lockout and brute-force protection."""
    
    # Configuration
    MAX_ATTEMPTS = 5  # Maximum failed attempts before lockout
    LOCKOUT_DURATION_MINUTES = 15  # Initial lockout duration
    ATTEMPT_WINDOW_MINUTES = 15  # Time window to count attempts
    MAX_LOCKOUT_DURATION_MINUTES = 60  # Maximum lockout duration (escalating)
    PROGRESSIVE_DELAY_BASE = 2  # Base seconds for progressive delay
    
    @classmethod
    def check_lockout(
        cls,
        identifier: str,
        identifier_type: str,
        attempt_type: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Check if an identifier (email/IP) is currently locked out.
        
        Args:
            identifier: Email address or IP address
            identifier_type: 'email' or 'ip'
            attempt_type: Type of attempt (otp_verify, login, etc.)
            db: Database session
            
        Returns:
            Dict with is_locked, remaining_seconds, and message
        """
        record = cls._get_or_create_record(identifier, identifier_type, attempt_type, db)
        
        if record.locked_until and record.locked_until > datetime.utcnow():
            remaining = (record.locked_until - datetime.utcnow()).total_seconds()
            return {
                'is_locked': True,
                'remaining_seconds': int(remaining),
                'message': f'Account temporarily locked. Please try again in {int(remaining / 60) + 1} minutes.',
                'attempt_count': record.attempt_count
            }
        
        return {
            'is_locked': False,
            'remaining_seconds': 0,
            'message': None,
            'attempt_count': record.attempt_count
        }
    
    @classmethod
    def record_failed_attempt(
        cls,
        identifier: str,
        identifier_type: str,
        attempt_type: str,
        db: Session,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a failed login/OTP attempt and check for lockout.
        
        Args:
            identifier: Email address or IP address
            identifier_type: 'email' or 'ip'
            attempt_type: Type of attempt (otp_verify, login, etc.)
            db: Database session
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Dict with is_locked, remaining_attempts, delay_seconds, and message
        """
        record = cls._get_or_create_record(identifier, identifier_type, attempt_type, db)
        
        # Check if we're outside the attempt window - reset if so
        window_start = datetime.utcnow() - timedelta(minutes=cls.ATTEMPT_WINDOW_MINUTES)
        if record.last_attempt_at and record.last_attempt_at < window_start:
            record.attempt_count = 0
            record.locked_until = None
        
        # Increment attempt count
        record.attempt_count += 1
        record.last_attempt_at = datetime.utcnow()
        record.ip_address = ip_address
        record.user_agent = user_agent
        
        # Check if we should lock the account
        if record.attempt_count >= cls.MAX_ATTEMPTS:
            # Calculate escalating lockout duration
            lockout_multiplier = min(record.attempt_count // cls.MAX_ATTEMPTS, 4)
            lockout_minutes = min(
                cls.LOCKOUT_DURATION_MINUTES * (2 ** lockout_multiplier),
                cls.MAX_LOCKOUT_DURATION_MINUTES
            )
            record.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
            
            # Log security event
            logger.warning(
                f"Account locked - Identifier: {identifier}, Type: {identifier_type}, "
                f"Attempts: {record.attempt_count}, Locked for: {lockout_minutes} minutes"
            )
            
            # Create audit log
            audit_log = AuditLog(
                action="account_locked",
                entity_type="security",
                details={
                    "identifier": identifier,
                    "identifier_type": identifier_type,
                    "attempt_type": attempt_type,
                    "attempt_count": record.attempt_count,
                    "lockout_minutes": lockout_minutes,
                    "ip_address": ip_address
                },
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(audit_log)
        
        db.commit()
        
        # Calculate progressive delay
        delay_seconds = cls._calculate_delay(record.attempt_count)
        remaining_attempts = max(0, cls.MAX_ATTEMPTS - record.attempt_count)
        
        if record.locked_until and record.locked_until > datetime.utcnow():
            remaining = (record.locked_until - datetime.utcnow()).total_seconds()
            return {
                'is_locked': True,
                'remaining_attempts': 0,
                'delay_seconds': delay_seconds,
                'remaining_seconds': int(remaining),
                'message': f'Too many failed attempts. Account locked for {int(remaining / 60) + 1} minutes.'
            }
        
        return {
            'is_locked': False,
            'remaining_attempts': remaining_attempts,
            'delay_seconds': delay_seconds,
            'remaining_seconds': 0,
            'message': f'{remaining_attempts} attempts remaining before lockout.' if remaining_attempts <= 2 else None
        }
    
    @classmethod
    def record_successful_attempt(
        cls,
        identifier: str,
        identifier_type: str,
        attempt_type: str,
        db: Session
    ) -> None:
        """
        Record a successful attempt and reset the lockout counter.
        
        Args:
            identifier: Email address or IP address
            identifier_type: 'email' or 'ip'
            attempt_type: Type of attempt
            db: Database session
        """
        record = db.query(FailedLoginAttempt).filter(
            and_(
                FailedLoginAttempt.identifier == identifier,
                FailedLoginAttempt.identifier_type == identifier_type,
                FailedLoginAttempt.attempt_type == attempt_type
            )
        ).first()
        
        if record:
            record.attempt_count = 0
            record.locked_until = None
            record.last_attempt_at = datetime.utcnow()
            db.commit()
    
    @classmethod
    def _get_or_create_record(
        cls,
        identifier: str,
        identifier_type: str,
        attempt_type: str,
        db: Session
    ) -> FailedLoginAttempt:
        """Get existing record or create new one."""
        record = db.query(FailedLoginAttempt).filter(
            and_(
                FailedLoginAttempt.identifier == identifier,
                FailedLoginAttempt.identifier_type == identifier_type,
                FailedLoginAttempt.attempt_type == attempt_type
            )
        ).first()
        
        if not record:
            record = FailedLoginAttempt(
                identifier=identifier,
                identifier_type=identifier_type,
                attempt_type=attempt_type,
                attempt_count=0
            )
            db.add(record)
            db.flush()
        
        return record
    
    @classmethod
    def _calculate_delay(cls, attempt_count: int) -> int:
        """
        Calculate progressive delay based on attempt count.
        Uses exponential backoff with a cap.
        """
        if attempt_count <= 1:
            return 0
        
        # Exponential backoff: 2, 4, 8, 16, 30 (capped)
        delay = cls.PROGRESSIVE_DELAY_BASE ** min(attempt_count - 1, 5)
        return min(delay, 30)  # Cap at 30 seconds
    
    @classmethod
    def cleanup_old_records(cls, db: Session, days: int = 7) -> int:
        """
        Clean up old failed attempt records.
        
        Args:
            db: Database session
            days: Number of days to keep records
            
        Returns:
            Number of deleted records
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.updated_at < cutoff
        ).delete()
        db.commit()
        return deleted
