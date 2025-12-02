"""Post-survey registration service for guest user conversion."""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import User, CustomerProfile, SurveyResponse, AuditLog, SimpleSession
from app.auth.utils import create_simple_session
from app.auth.schemas import SimpleAuthResponse


class PostRegistrationService:
    """Service for handling post-survey registration and guest data migration."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_guest_user(
        self,
        email: str,
        date_of_birth: datetime,
        guest_survey_data: Dict[str, Any],
        subscribe_to_updates: bool = False
    ) -> SimpleAuthResponse:
        """
        Register a guest user and migrate their survey data.
        
        Args:
            email: User's email address
            date_of_birth: User's date of birth
            guest_survey_data: Survey data from localStorage
            subscribe_to_updates: Whether user wants to receive updates
            
        Returns:
            SimpleAuthResponse with user data and session info
            
        Raises:
            ValueError: If user already exists or data is invalid
            IntegrityError: If database constraints are violated
        """
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.email == email).first()
            
            if existing_user:
                # If user exists but doesn't have date_of_birth set, update it
                if existing_user.date_of_birth is None:
                    existing_user.date_of_birth = date_of_birth
                    self.db.commit()
                    
                    # Create session and return existing user data
                    return await self._create_user_session(existing_user)
                else:
                    # User already exists with date_of_birth - check if it matches
                    user_dob = existing_user.date_of_birth
                    if hasattr(user_dob, 'date'):
                        user_dob = user_dob.date()
                    
                    if user_dob != date_of_birth.date():
                        raise ValueError("An account with this email already exists with a different date of birth")
                    
                    # Dates match - create session and return user data
                    return await self._create_user_session(existing_user)
            
            # Create new user
            new_user = User(
                email=email,
                username=self._generate_username_from_email(email),
                hashed_password="",  # No password for simple auth users
                date_of_birth=date_of_birth,
                is_active=True,
                is_admin=False
            )
            
            self.db.add(new_user)
            self.db.flush()  # Get the user ID without committing
            
            # Create customer profile from guest survey data
            profile_data = guest_survey_data.get('profile', {})
            if profile_data:
                customer_profile = self._create_customer_profile(new_user.id, profile_data)
                self.db.add(customer_profile)
                self.db.flush()
            
            # Migrate survey response data
            if guest_survey_data.get('responses') and guest_survey_data.get('totalScore'):
                survey_response = self._create_survey_response(
                    new_user.id,
                    customer_profile.id if profile_data else None,
                    guest_survey_data
                )
                self.db.add(survey_response)

            # Link Financial Clinic survey if exists
            if guest_survey_data.get('survey_response_id'):
                from app.models import FinancialClinicResponse
                fc_response = self.db.query(FinancialClinicResponse).filter(
                    FinancialClinicResponse.id == guest_survey_data['survey_response_id']
                ).first()
                if fc_response and fc_response.user_id is None:
                    fc_response.user_id = new_user.id
                    # Also link the profile if it exists
                    if fc_response.profile:
                        if not fc_response.profile.email:
                            fc_response.profile.email = email
            
            # Log registration
            audit_log = AuditLog(
                user_id=new_user.id,
                action="post_survey_registration",
                entity_type="user",
                entity_id=new_user.id,
                details={
                    "email": email,
                    "registration_type": "post_survey",
                    "subscribe_to_updates": subscribe_to_updates,
                    "has_survey_data": bool(guest_survey_data.get('responses'))
                }
            )
            self.db.add(audit_log)
            
            # Commit all changes
            self.db.commit()
            self.db.refresh(new_user)
            
            # Create session and return user data
            return await self._create_user_session(new_user)
            
        except IntegrityError as e:
            self.db.rollback()
            if "email" in str(e):
                raise ValueError("An account with this email already exists")
            elif "username" in str(e):
                # Try with a different username
                new_user.username = self._generate_username_from_email(email, suffix=True)
                self.db.add(new_user)
                self.db.commit()
                return await self._create_user_session(new_user)
            else:
                raise ValueError("Registration failed due to data constraints")
        except Exception as e:
            self.db.rollback()
            raise e
    
    def _generate_username_from_email(self, email: str, suffix: bool = False) -> str:
        """Generate a username from email address."""
        base_username = email.split('@')[0].lower()
        # Remove non-alphanumeric characters except underscore and dash
        base_username = ''.join(c for c in base_username if c.isalnum() or c in ['_', '-'])
        
        if suffix:
            # Add timestamp suffix to make it unique
            timestamp = str(int(datetime.now().timestamp()))[-6:]
            return f"{base_username}_{timestamp}"
        
        return base_username
    
    def _create_customer_profile(self, user_id: int, profile_data: Dict[str, Any]) -> CustomerProfile:
        """Create a customer profile from guest survey data."""
        # Map frontend profile fields to database fields
        return CustomerProfile(
            user_id=user_id,
            first_name=profile_data.get('name', '').split(' ')[0] or 'User',
            last_name=' '.join(profile_data.get('name', '').split(' ')[1:]) or 'Profile',
            age=profile_data.get('age', 25),
            gender=profile_data.get('gender', 'Prefer not to say'),
            nationality=profile_data.get('nationality', 'UAE'),
            emirate=profile_data.get('residence', 'Dubai'),
            employment_status=profile_data.get('employmentStatus', 'Employed'),
            industry=profile_data.get('employmentSector'),
            monthly_income=profile_data.get('incomeRange', 'AED 5,000 - 10,000'),
            household_size=1,  # Default value
            children=profile_data.get('children', 'No'),
            phone_number=None,
            preferred_language='en'
        )
    
    def _create_survey_response(
        self,
        user_id: int,
        customer_profile_id: Optional[int],
        guest_survey_data: Dict[str, Any]
    ) -> SurveyResponse:
        """Create a survey response from guest survey data."""
        # Convert frontend responses to backend format
        responses_dict = {}
        for response in guest_survey_data.get('responses', []):
            responses_dict[response['questionId']] = response['value']
        
        # Extract pillar scores or use defaults
        pillar_scores = guest_survey_data.get('pillarScores', [])
        
        # Map pillar scores to database fields
        budgeting_score = 0
        savings_score = 0
        debt_management_score = 0
        financial_planning_score = 0
        investment_knowledge_score = 0
        
        for pillar in pillar_scores:
            pillar_name = pillar.get('pillar', '')
            score = pillar.get('score', 0)
            
            if pillar_name == 'income_stream':
                budgeting_score = score
            elif pillar_name == 'savings_habit':
                savings_score = score
            elif pillar_name == 'debt_management':
                debt_management_score = score
            elif pillar_name == 'retirement_planning':
                financial_planning_score = score
            elif pillar_name == 'future_planning':
                investment_knowledge_score = score
        
        return SurveyResponse(
            user_id=user_id,
            customer_profile_id=customer_profile_id,
            responses=responses_dict,
            overall_score=guest_survey_data.get('totalScore', 0),
            budgeting_score=budgeting_score,
            savings_score=savings_score,
            debt_management_score=debt_management_score,
            financial_planning_score=financial_planning_score,
            investment_knowledge_score=investment_knowledge_score,
            risk_tolerance='moderate',  # Default value
            financial_goals=None,
            completion_time=None,
            survey_version='2.0',
            language='en'
        )
    
    async def _create_user_session(self, user: User) -> SimpleAuthResponse:
        """Create a simple session for the user and return response data."""
        # Create simple session
        session_id, expires_at = create_simple_session(user.id)
        
        # Store session in database
        simple_session = SimpleSession(
            user_id=user.id,
            session_id=session_id,
            expires_at=expires_at
        )
        self.db.add(simple_session)
        
        # Get user's survey history
        survey_responses = self.db.query(SurveyResponse).filter(
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
        
        # Log session creation
        audit_log = AuditLog(
            user_id=user.id,
            action="post_registration_login",
            entity_type="user",
            entity_id=user.id,
            details={"email": user.email, "session_id": session_id}
        )
        self.db.add(audit_log)
        self.db.commit()
        
        return SimpleAuthResponse(
            user_id=user.id,
            email=user.email,
            session_id=session_id,
            survey_history=survey_history,
            expires_at=expires_at
        )


class DataMigrationResult:
    """Result object for data migration operations."""
    
    def __init__(self, success: bool, message: str, migrated_items: int = 0):
        self.success = success
        self.message = message
        self.migrated_items = migrated_items


class UserRegistrationResult:
    """Result object for user registration operations."""
    
    def __init__(self, success: bool, user_id: Optional[int] = None, message: str = ""):
        self.success = success
        self.user_id = user_id
        self.message = message