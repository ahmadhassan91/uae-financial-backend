from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_admin_user
from app.models import User, LocalizedContent, SurveyResponse, CustomerProfile, CompanyTracker
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import csv
import io
import traceback

simple_admin_router = APIRouter(prefix="/admin/simple", tags=["admin-simple"])

def filter_unique_users(responses):
    """
        
    Returns:
        List of FinancialClinicResponse objects with only the latest submission per email
    """
    email_to_latest = {}
    
    for response in responses:
        if response.profile and response.profile.email:
            email = response.profile.email
            if email not in email_to_latest or response.created_at > email_to_latest[email].created_at:
                email_to_latest[email] = response
    
    return list(email_to_latest.values())

def apply_demographic_filters(query, filters: Dict[str, List[str]], db: Session):
    """
    Apply demographic filters to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object (already joined with FinancialClinicProfile)
        filters: Dictionary of filter parameters
        db: Database session
        
    Returns:
        Filtered query
    """
    from app.models import FinancialClinicProfile, CompanyTracker
    
    # Age groups filter - Financial Clinic uses date_of_birth, so we need to calculate age
    if filters.get('age_groups'):
        age_conditions = []
        for age_group in filters['age_groups']:
            # For Financial Clinic, we need to parse the date_of_birth field
            # This is complex to do in SQL with DD/MM/YYYY format, so we'll skip age filtering for now
            # TODO: Implement age calculation from date_of_birth in DD/MM/YYYY format
            pass
        if age_conditions:
            query = query.filter(or_(*age_conditions))
    
    # Gender filter
    if filters.get('genders'):
        query = query.filter(FinancialClinicProfile.gender.in_(filters['genders']))
    
    # Nationality filter
    if filters.get('nationalities'):
        query = query.filter(FinancialClinicProfile.nationality.in_(filters['nationalities']))
    
    # Emirate filter
    if filters.get('emirates'):
        query = query.filter(FinancialClinicProfile.emirate.in_(filters['emirates']))
    
    # Employment status filter
    if filters.get('employment_statuses'):
        query = query.filter(FinancialClinicProfile.employment_status.in_(filters['employment_statuses']))
    
    # Income range filter
    if filters.get('income_ranges'):
        query = query.filter(FinancialClinicProfile.income_range.in_(filters['income_ranges']))
    
    # Children filter
    if filters.get('children'):
        children_conditions = []
        for child_option in filters['children']:
            if child_option == '0':
                children_conditions.append(FinancialClinicProfile.children == 0)
            elif child_option == '1':
                children_conditions.append(FinancialClinicProfile.children == 1)
            elif child_option == '2':
                children_conditions.append(FinancialClinicProfile.children == 2)
            elif child_option == '3':
                children_conditions.append(FinancialClinicProfile.children == 3)
            elif child_option == '4':
                children_conditions.append(FinancialClinicProfile.children == 4)
            elif child_option == '5+':
                children_conditions.append(FinancialClinicProfile.children >= 5)
        if children_conditions:
            query = query.filter(or_(*children_conditions))
    
    # Company filter
    if filters.get('companies'):
        # Get company IDs from company names or URLs
        company_trackers = db.query(CompanyTracker).filter(
            or_(
                CompanyTracker.company_name.in_(filters['companies']),
                CompanyTracker.unique_url.in_(filters['companies'])
            )
        ).all()
        company_ids = [c.id for c in company_trackers]
        if company_ids:
            from app.models import FinancialClinicResponse
            query = query.filter(FinancialClinicResponse.company_tracker_id.in_(company_ids))
    
    return query

def apply_date_range_filter(query, date_range: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Apply date range filtering to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        date_range: Predefined date range ('7d', '30d', '90d', '1y', 'ytd', 'all')
        start_date: Custom start date (YYYY-MM-DD format)
        end_date: Custom end date (YYYY-MM-DD format)
        
    Returns:
        Filtered query
    """
    from app.models import FinancialClinicResponse
    
    # If custom date range is provided, use it
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # Include end date
            query = query.filter(
                FinancialClinicResponse.created_at >= start_dt,
                FinancialClinicResponse.created_at < end_dt
            )
        except ValueError:
            # Invalid date format, skip filtering
            pass
        return query
    
    # Apply predefined date range filters
    now = datetime.now()
    
    if date_range == "7d":
        start_date = now - timedelta(days=7)
        query = query.filter(FinancialClinicResponse.created_at >= start_date)
    elif date_range == "30d":
        start_date = now - timedelta(days=30)
        query = query.filter(FinancialClinicResponse.created_at >= start_date)
    elif date_range == "90d":
        start_date = now - timedelta(days=90)
        query = query.filter(FinancialClinicResponse.created_at >= start_date)
    elif date_range == "1y":
        start_date = now - timedelta(days=365)
        query = query.filter(FinancialClinicResponse.created_at >= start_date)
    elif date_range == "ytd":
        # Year to date - from January 1st of current year
        start_date = datetime(now.year, 1, 1)
        query = query.filter(FinancialClinicResponse.created_at >= start_date)
    elif date_range == "all":
        # No date filtering for "all time"
        pass
    
    return query

def parse_filter_params(
    age_groups: Optional[str] = None,
    genders: Optional[str] = None,
    nationalities: Optional[str] = None,
    emirates: Optional[str] = None,
    employment_statuses: Optional[str] = None,
    income_ranges: Optional[str] = None,
    children: Optional[str] = None,
    companies: Optional[str] = None
) -> Dict[str, List[str]]:
    """Parse comma-separated filter parameters into lists."""
    filters = {}
    
    if age_groups:
        filters['age_groups'] = [ag.strip() for ag in age_groups.split(',')]
    if genders:
        filters['genders'] = [g.strip() for g in genders.split(',')]
    if nationalities:
        filters['nationalities'] = [n.strip() for n in nationalities.split(',')]
    if emirates:
        filters['emirates'] = [e.strip() for e in emirates.split(',')]
    if employment_statuses:
        filters['employment_statuses'] = [es.strip() for es in employment_statuses.split(',')]
    if income_ranges:
        filters['income_ranges'] = [ir.strip() for ir in income_ranges.split(',')]
    if children:
        filters['children'] = [c.strip() for c in children.split(',')]
    if companies:
        filters['companies'] = [c.strip() for c in companies.split(',')]
    
    return filters

@simple_admin_router.get("/localized-content")
async def get_simple_localized_content(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Simple endpoint to get localized content without complex schemas."""
    try:
        # Get all localized content
        content_items = db.query(LocalizedContent).filter(
            LocalizedContent.is_active == True
        ).order_by(
            LocalizedContent.content_type,
            LocalizedContent.content_id,
            LocalizedContent.language
        ).limit(100).all()
        
        # Convert to simple dict format
        result = []
        for item in content_items:
            result.append({
                "id": item.id,
                "content_type": item.content_type,
                "content_id": item.content_id,
                "language": item.language,
                "title": item.title,
                "text": item.text[:100] + "..." if item.text and len(item.text) > 100 else item.text,
                "is_active": item.is_active,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            })
        
        return {
            "content": result,
            "total": len(result),
            "message": "Simple admin endpoint working"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "content": [],
            "total": 0
        }

@simple_admin_router.get("/analytics")
async def get_simple_analytics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Simple analytics endpoint."""
    try:
        # Get basic counts
        total_content = db.query(LocalizedContent).count()
        english_content = db.query(LocalizedContent).filter(LocalizedContent.language == 'en').count()
        arabic_content = db.query(LocalizedContent).filter(LocalizedContent.language == 'ar').count()
        
        return {
            "total_content_items": total_content,
            "translated_items": arabic_content,
            "english_items": english_content,
            "arabic_items": arabic_content,
            "translation_coverage": {
                "ar": arabic_content / english_content if english_content > 0 else 0
            },
            "pending_translations": max(0, english_content - arabic_content),
            "quality_scores": {
                "ar": 0.85,
                "en": 0.90,
                "overall": 0.87
            },
            "most_requested_content": [
                {"content_type": "question", "content_id": "q1", "request_count": 25},
                {"content_type": "question", "content_id": "q2", "request_count": 20},
                {"content_type": "ui", "content_id": "welcome_message", "request_count": 15}
            ],
            "analysis_period_days": 30,
            "message": "Simple analytics working"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_content_items": 0
        }

@simple_admin_router.get("/export-csv")
async def export_simple_admin_csv(
    date_range: str = "30d",
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """Export filtered financial clinic responses as CSV (admin only)."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile, AuditLog

        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )

        # Build base query
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )

        # Apply date filters
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(FinancialClinicResponse.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(FinancialClinicResponse.created_at <= end_dt)

        # Apply other demographic filters
        query = apply_demographic_filters(query, filters, db)

        # Optionally filter unique users
        responses = query.order_by(FinancialClinicResponse.created_at.desc()).all()
        if unique_users_only:
            responses = filter_unique_users(responses)

        # Helper function to calculate age from DOB string (DD/MM/YYYY)
        def calculate_age(dob_str):
            try:
                from datetime import datetime
                dob = datetime.strptime(dob_str, '%d/%m/%Y')
                today = datetime.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                return age
            except:
                return ''
        
        # Helper function to get category score from JSON
        def get_category_score(category_scores, category_name):
            if not category_scores:
                return 0
            try:
                # category_scores is stored as JSON with structure like:
                # {"income_stream": {"score": 10, ...}, "savings_habit": {...}, ...}
                if isinstance(category_scores, dict):
                    category_data = category_scores.get(category_name, {})
                    if isinstance(category_data, dict):
                        return category_data.get('score', 0)
                return 0
            except:
                return 0
        
        # Prepare CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header matching reference CSV structure
        writer.writerow([
            'ID', 'Name', 'Email', 'Age', 'Gender', 'Nationality', 'Emirate', 'Children',
            'Employment Status', 'Income Range', 'Company', 'Total Score', 'Status Band',
            'Questions Answered', 'Income Stream Score', 'Savings Habit Score',
            'Debt Management Score', 'Retirement Planning Score', 'Financial Protection Score',
            'Financial Knowledge Score', 'Submission Date'
        ])

        for r in responses:
            profile = db.query(FinancialClinicProfile).filter(FinancialClinicProfile.id == r.profile_id).first()
            
            # Extract category scores from JSON
            income_stream_score = get_category_score(r.category_scores, 'income_stream')
            savings_habit_score = get_category_score(r.category_scores, 'savings_habit')
            debt_management_score = get_category_score(r.category_scores, 'debt_management')
            retirement_planning_score = get_category_score(r.category_scores, 'retirement_planning')
            financial_protection_score = get_category_score(r.category_scores, 'financial_protection')
            financial_knowledge_score = get_category_score(r.category_scores, 'financial_knowledge')
            
            writer.writerow([
                r.id,
                profile.name if profile else '',
                profile.email if profile else '',
                calculate_age(profile.date_of_birth) if profile and profile.date_of_birth else '',
                profile.gender if profile else '',
                profile.nationality if profile else '',
                profile.emirate if profile else '',
                profile.children if profile else '',
                profile.employment_status if profile else '',
                profile.income_range if profile else '',
                '',  # Company (from company_tracker_id if needed)
                round(r.total_score, 2) if r.total_score else 0,
                r.status_band if r.status_band else '',
                r.questions_answered if r.questions_answered else 0,
                income_stream_score,
                savings_habit_score,
                debt_management_score,
                retirement_planning_score,
                financial_protection_score,
                financial_knowledge_score,
                r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ''
            ])

        # Audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            action="simple_admin_export_csv",
            entity_type="financial_clinic_responses",
            details={"exported_count": len(responses), "filters": filters}
        )
        db.add(audit_log)
        db.commit()

        output.seek(0)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"financial_clinic_responses_{timestamp}.csv"

        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=str(e))


@simple_admin_router.get("/export-excel")
async def export_simple_admin_excel(
    date_range: str = "30d",
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """Export filtered financial clinic responses as Excel (admin only)."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile, AuditLog

        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )

        # Build base query using correct Financial Clinic models
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(FinancialClinicResponse.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(FinancialClinicResponse.created_at <= end_dt)

        query = apply_demographic_filters(query, filters, db)

        responses = query.order_by(FinancialClinicResponse.created_at.desc()).all()
        if unique_users_only:
            responses = filter_unique_users(responses)

        # Helper function to calculate age from DOB string (DD/MM/YYYY)
        def calculate_age(dob_str):
            try:
                from datetime import datetime
                dob = datetime.strptime(dob_str, '%d/%m/%Y')
                today = datetime.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                return age
            except:
                return ''
        
        # Helper function to get category score from JSON
        def get_category_score(category_scores, category_name):
            if not category_scores:
                return 0
            try:
                if isinstance(category_scores, dict):
                    category_data = category_scores.get(category_name, {})
                    if isinstance(category_data, dict):
                        return category_data.get('score', 0)
                return 0
            except:
                return 0

        # Build dataframe rows
        rows = []
        for r in responses:
            profile = db.query(FinancialClinicProfile).filter(FinancialClinicProfile.id == r.profile_id).first()
            
            # Extract category scores from JSON
            income_stream_score = get_category_score(r.category_scores, 'income_stream')
            savings_habit_score = get_category_score(r.category_scores, 'savings_habit')
            debt_management_score = get_category_score(r.category_scores, 'debt_management')
            retirement_planning_score = get_category_score(r.category_scores, 'retirement_planning')
            financial_protection_score = get_category_score(r.category_scores, 'financial_protection')
            financial_knowledge_score = get_category_score(r.category_scores, 'financial_knowledge')
            
            rows.append({
                'id': r.id,
                'name': profile.name if profile else '',
                'email': profile.email if profile else '',
                'age': calculate_age(profile.date_of_birth) if profile and profile.date_of_birth else '',
                'gender': profile.gender if profile else '',
                'nationality': profile.nationality if profile else '',
                'emirate': profile.emirate if profile else '',
                'children': profile.children if profile else '',
                'employment_status': profile.employment_status if profile else '',
                'income_range': profile.income_range if profile else '',
                'company': '',  # Company (from company_tracker_id if needed)
                'total_score': round(r.total_score, 2) if r.total_score else 0,
                'status_band': r.status_band if r.status_band else '',
                'questions_answered': r.questions_answered if r.questions_answered else 0,
                'income_stream_score': income_stream_score,
                'savings_habit_score': savings_habit_score,
                'debt_management_score': debt_management_score,
                'retirement_planning_score': retirement_planning_score,
                'financial_protection_score': financial_protection_score,
                'financial_knowledge_score': financial_knowledge_score,
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ''
            })

        # Create Excel file
        bio = io.BytesIO()
        
        # Use openpyxl directly for better compatibility
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Financial Clinic Responses"
        
        # Add headers matching reference CSV structure
        headers = [
            'ID', 'Name', 'Email', 'Age', 'Gender', 'Nationality', 'Emirate', 'Children',
            'Employment Status', 'Income Range', 'Company', 'Total Score', 'Status Band',
            'Questions Answered', 'Income Stream Score', 'Savings Habit Score',
            'Debt Management Score', 'Retirement Planning Score', 'Financial Protection Score',
            'Financial Knowledge Score', 'Submission Date'
        ]
        ws.append(headers)
        
        # Add data rows
        for row in rows:
            ws.append([
                row['id'],
                row['name'], 
                row['email'],
                row['age'],
                row['gender'],
                row['nationality'],
                row['emirate'],
                row['children'],
                row['employment_status'],
                row['income_range'],
                row['company'],
                row['total_score'],
                row['status_band'],
                row['questions_answered'],
                row['income_stream_score'],
                row['savings_habit_score'],
                row['debt_management_score'],
                row['retirement_planning_score'],
                row['financial_protection_score'],
                row['financial_knowledge_score'],
                row['created_at']
            ])
        
        wb.save(bio)
        bio.seek(0)

        # Audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            action="simple_admin_export_excel",
            entity_type="financial_clinic_responses",
            details={"exported_count": len(responses), "filters": filters}
        )
        db.add(audit_log)
        db.commit()

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"financial_clinic_responses_{timestamp}.xlsx"

        return StreamingResponse(
            bio,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=str(e))

@simple_admin_router.get("/survey-submissions")
async def get_survey_submissions(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    limit: int = 50,
    offset: int = 0,
    survey_type: str = "all"  # "all", "old", "financial_clinic"
):
    """Get survey submissions for admin dashboard - supports BOTH old surveys and Financial Clinic."""
    try:
        from app.models import FinancialClinicProfile, FinancialClinicResponse
        
        result = []
        
        # Fetch Financial Clinic submissions (NEW SYSTEM)
        if survey_type in ["all", "financial_clinic"]:
            fc_submissions = db.query(FinancialClinicResponse).join(
                FinancialClinicProfile,
                FinancialClinicResponse.profile_id == FinancialClinicProfile.id
            ).order_by(
                FinancialClinicResponse.created_at.desc()
            ).limit(limit if survey_type == "financial_clinic" else limit // 2).all()
            
            for submission in fc_submissions:
                profile = submission.profile
                
                # Parse age from DOB (format: DD/MM/YYYY)
                age = None
                if profile.date_of_birth:
                    try:
                        from datetime import datetime
                        # Split DD/MM/YYYY
                        parts = profile.date_of_birth.strip().split('/')
                        if len(parts) == 3:
                            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                            
                            # Handle invalid dates (like Feb 29 on non-leap years)
                            # For invalid dates, just use Jan 1 of that year to get approximate age
                            try:
                                birth_date = datetime(year, month, day)
                            except ValueError:
                                # Invalid date, use Jan 1 as approximation
                                birth_date = datetime(year, 1, 1)
                            
                            today = datetime.now()
                            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    except Exception as e:
                        # Log the error for debugging
                        print(f"Error parsing DOB '{profile.date_of_birth}': {e}")
                        age = None
                
                result.append({
                    "id": f"fc_{submission.id}",
                    "survey_type": "financial_clinic",
                    "user_id": None,
                    "user_type": "financial_clinic",
                    "user_info": None,
                    "profile_info": {
                        "name": profile.name,
                        "age": age,
                        "gender": profile.gender,
                        "nationality": profile.nationality,
                        "emirate": profile.emirate,
                        "children": profile.children,
                        "employment": profile.employment_status,
                        "income": profile.income_range,
                        "email": profile.email
                    },
                    "overall_score": submission.total_score,
                    "status_band": submission.status_band,
                    "category_scores": submission.category_scores,
                    "budgeting_score": submission.category_scores.get('income_stream', 0) if submission.category_scores else 0,
                    "savings_score": submission.category_scores.get('savings_habit', 0) if submission.category_scores else 0,
                    "debt_management_score": submission.category_scores.get('debt_management', 0) if submission.category_scores else 0,
                    "financial_planning_score": submission.category_scores.get('retirement_planning', 0) if submission.category_scores else 0,
                    "investment_knowledge_score": 0,
                    "risk_tolerance": None,
                    "financial_goals": None,
                    "completion_time": None,
                    "survey_version": "financial_clinic_v1",
                    "created_at": submission.created_at.isoformat() if submission.created_at else None,
                    "response_count": submission.questions_answered,
                    "company_tracker_id": submission.company_tracker_id
                })
        
        # Fetch OLD survey submissions (if requested)
        if survey_type in ["all", "old"]:
            old_submissions = db.query(SurveyResponse).order_by(
                SurveyResponse.created_at.desc()
            ).limit(limit if survey_type == "old" else limit // 2).all()
            
            for submission in old_submissions:
                # Get user info if available
                user_info = None
                if submission.user_id:
                    user = db.query(User).filter(User.id == submission.user_id).first()
                    if user:
                        user_info = {
                            "id": user.id,
                            "email": user.email,
                            "is_admin": user.is_admin
                        }
                
                # Get profile info if available
                profile_info = None
                if submission.customer_profile_id:
                    profile = db.query(CustomerProfile).filter(
                        CustomerProfile.id == submission.customer_profile_id
                    ).first()
                    if profile:
                        profile_info = {
                            "age": profile.age,
                            "gender": profile.gender,
                            "children": profile.children,
                            "employment": profile.employment_status,
                            "income": profile.monthly_income
                        }
                
                result.append({
                    "id": f"old_{submission.id}",
                    "survey_type": "old_survey",
                    "user_id": submission.user_id,
                    "user_type": "authenticated" if submission.user_id else "guest",
                    "user_info": user_info,
                    "profile_info": profile_info,
                    "overall_score": submission.overall_score,
                    "status_band": None,
                    "category_scores": None,
                    "budgeting_score": submission.budgeting_score,
                    "savings_score": submission.savings_score,
                    "debt_management_score": submission.debt_management_score,
                    "financial_planning_score": submission.financial_planning_score,
                    "investment_knowledge_score": submission.investment_knowledge_score,
                    "risk_tolerance": submission.risk_tolerance,
                    "financial_goals": submission.financial_goals,
                    "completion_time": submission.completion_time,
                    "survey_version": submission.survey_version,
                    "created_at": submission.created_at.isoformat() if submission.created_at else None,
                    "response_count": len(submission.responses) if submission.responses else 0,
                    "company_tracker_id": None
                })
        
        # Sort all results by created_at
        result.sort(key=lambda x: x['created_at'] if x['created_at'] else '', reverse=True)
        
        # Apply pagination
        paginated_result = result[offset:offset+limit]
        
        # Get total counts
        total_fc = db.query(FinancialClinicResponse).count() if survey_type in ["all", "financial_clinic"] else 0
        total_old = db.query(SurveyResponse).count() if survey_type in ["all", "old"] else 0
        total_submissions = total_fc + total_old if survey_type == "all" else (total_fc if survey_type == "financial_clinic" else total_old)
        
        return {
            "submissions": paginated_result,
            "total": total_submissions,
            "financial_clinic_count": total_fc,
            "old_survey_count": total_old,
            "page_size": limit,
            "offset": offset,
            "survey_type": survey_type,
            "message": f"Found {len(paginated_result)} submissions ({total_fc} Financial Clinic, {total_old} Old Surveys)"
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "submissions": [],
            "total": 0
        }

@simple_admin_router.get("/question-variations-simple")
async def get_variations_for_companies(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get question variations formatted for company assignment.
    Returns active variations grouped by base question for easy selection.
    """
    try:
        from app.models import QuestionVariation
        
        # Get all active question variations
        variations = db.query(QuestionVariation).filter(
            QuestionVariation.is_active == True
        ).order_by(
            QuestionVariation.base_question_id,
            QuestionVariation.language
        ).all()
        
        # Group by base question for easy selection
        by_question = {}
        for v in variations:
            if v.base_question_id not in by_question:
                by_question[v.base_question_id] = []
            by_question[v.base_question_id].append({
                "id": v.id,
                "name": v.variation_name,
                "language": v.language,
                "preview": v.text[:100] + "..." if len(v.text) > 100 else v.text
            })
        
        return {
            "variations_by_question": by_question,
            "total_variations": len(variations),
            "questions_with_variations": len(by_question)
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "variations_by_question": {}
        }

@simple_admin_router.get("/filter-options")
async def get_filter_options(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get all available filter options for Financial Clinic dashboard.
    Returns ALL possible options exactly as they appear in the survey form,
    not just values that exist in the database.
    """
    try:
        from app.models import CompanyTracker
        
        # Return ALL possible options from the survey form
        # These match exactly what users can select in /financial-clinic/page.tsx
        all_age_groups = ["<18", "18-25", "25-35", "35-45", "45-60", "65+"]
        all_genders = ["Male", "Female"]
        all_nationalities = ["Emirati", "Non-Emirati"]
        all_emirates = [
            "Dubai",
            "Abu Dhabi", 
            "Sharjah",
            "Ajman",
            "Al Ain",
            "Ras Al Khaimah / Fujairah / UAQ / Outside UAE"
        ]
        all_employment_statuses = ["Employed", "Self-Employed", "Unemployed"]
        all_income_ranges = [
            "Below 5,000",
            "5,000 to 10,000",
            "10,000 to 20,000",
            "20,000 to 30,000",
            "30,000 to 40,000",
            "40,000 to 50,000",
            "50,000 to 100,000",
            "Above 100,000"
        ]
        all_children_options = ["0", "1", "2", "3", "4", "5+"]
        
        # Get companies (these are dynamic)
        companies = db.query(CompanyTracker).filter(
            CompanyTracker.is_active == True
        ).order_by(CompanyTracker.company_name).all()
        
        company_list = [
            {
                "id": c.id,
                "name": c.company_name,
                "unique_url": c.unique_url
            }
            for c in companies
        ]
        
        return {
            "age_groups": all_age_groups,
            "genders": all_genders,
            "nationalities": all_nationalities,
            "emirates": all_emirates,
            "employment_statuses": all_employment_statuses,
            "income_ranges": all_income_ranges,
            "children_options": all_children_options,
            "companies": company_list
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "age_groups": ["<18", "18-25", "25-35", "35-45", "45-60", "65+"],
            "genders": ["Male", "Female"],
            "nationalities": ["Emirati", "Non-Emirati"],
            "emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Al Ain", "Ras Al Khaimah / Fujairah / UAQ / Outside UAE"],
            "employment_statuses": ["Employed", "Self-Employed", "Unemployed"],
            "income_ranges": ["Below 5,000", "5,000 to 10,000", "10,000 to 20,000", "20,000 to 30,000", "30,000 to 40,000", "40,000 to 50,000", "50,000 to 100,000", "Above 100,000"],
            "children_options": ["0", "1", "2", "3", "4", "5+"],
            "companies": []
        }

@simple_admin_router.get("/overview-metrics")
async def get_overview_metrics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    date_range: str = "30d",
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None)
):
    """Get overview metrics (KPIs) for the admin dashboard."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile
        
        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )
        
        # Get all responses with filters applied
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply date range filtering
        query = apply_date_range_filter(query, date_range, start_date, end_date)
        
        # Apply demographic filters
        query = apply_demographic_filters(query, filters, db)
        
        responses = query.all()
        
        # Get total responses (before unique filter)
        all_responses_count = len(responses)
        
        # Apply unique user filter only if requested
        if unique_users_only:
            responses = filter_unique_users(responses)
        
        total_responses = len(responses)
        
        if total_responses == 0:
            return {
                "total_responses": 0,
                "total_submissions": 0,
                "unique_completions": 0,
                "cases_completed_percentage": 0.0,
                "unique_completion_percentage": 0.0,
                "average_score": 0,
                "excellent_count": 0,
                "good_count": 0,
                "needs_improvement_count": 0,
                "at_risk_count": 0
            }
        
        # Calculate metrics
        total_score = sum(r.total_score for r in responses)
        average_score = total_score / total_responses if total_responses > 0 else 0
        
        # Count by status band
        excellent_count = sum(1 for r in responses if r.status_band == "Excellent")
        good_count = sum(1 for r in responses if r.status_band == "Good")
        needs_improvement_count = sum(1 for r in responses if r.status_band == "Needs Improvement")
        at_risk_count = sum(1 for r in responses if r.status_band == "At Risk")
        
        # Calculate completion percentages
        # For "cases completed" we use unique responses as the success metric
        cases_completed_percentage = 100.0  # All retrieved responses are considered "completed" in Financial Clinic
        unique_completion_percentage = (total_responses / all_responses_count * 100) if all_responses_count > 0 else 0.0
        
        return {
            "total_responses": total_responses,  # Keep for backward compatibility
            "total_submissions": all_responses_count,  # Total including duplicates
            "unique_completions": total_responses,  # Unique users who completed
            "cases_completed_percentage": round(cases_completed_percentage, 2),
            "unique_completion_percentage": round(unique_completion_percentage, 2),
            "average_score": round(average_score, 2),
            "excellent_count": excellent_count,
            "good_count": good_count,
            "needs_improvement_count": needs_improvement_count,
            "at_risk_count": at_risk_count
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@simple_admin_router.get("/score-distribution")
async def get_score_distribution(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    date_range: str = "30d",
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None)
):
    """Get score distribution by status bands."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile
        
        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )
        
        # Get all responses with filters applied
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply date range filtering
        query = apply_date_range_filter(query, date_range, start_date, end_date)
        
        # Apply demographic filters
        query = apply_demographic_filters(query, filters, db)
        
        responses = query.all()
        
        # Apply unique user filter only if requested
        if unique_users_only:
            responses = filter_unique_users(responses)
        
        # Count by status band
        distribution = {}
        for response in responses:
            status = response.status_band
            distribution[status] = distribution.get(status, 0) + 1
        
        return {
            "total": len(responses),
            "distribution": [
                {"status_band": status, "count": count}
                for status, count in distribution.items()
            ]
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@simple_admin_router.get("/category-performance")
async def get_category_performance(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    date_range: str = "30d",
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None)
):
    """Get category performance (6 categories)."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile
        
        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )
        
        # Get all responses with filters applied
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply demographic filters
        query = apply_demographic_filters(query, filters, db)
        
        responses = query.all()
        
        # Apply unique user filter only if requested
        if unique_users_only:
            responses = filter_unique_users(responses)
        unique_responses = responses
        
        # Categories mapping: database name -> API name
        # Database stores: "Income Stream", "Savings Habit", etc.
        # API returns: "income_stream", "savings_habit", etc.
        category_mapping = {
            "Income Stream": "income_stream",
            "Savings Habit": "savings_habit",
            "Emergency Savings": "emergency_savings",
            "Debt Management": "debt_management",
            "Retirement Planning": "retirement_planning",
            "Protecting Your Family": "financial_protection",
            "Financial Knowledge": "financial_knowledge"
        }
        
        # Calculate average score per category
        category_totals = {}
        category_counts = {}
        category_max_possible = {}
        
        for response in unique_responses:
            if response.category_scores and isinstance(response.category_scores, dict):
                for db_category, api_category in category_mapping.items():
                    if db_category in response.category_scores:
                        cat_data = response.category_scores[db_category]
                        
                        # Initialize if not exists
                        if api_category not in category_totals:
                            category_totals[api_category] = 0
                            category_counts[api_category] = 0
                            category_max_possible[api_category] = 0
                        
                        # Handle both dict and numeric values
                        if isinstance(cat_data, dict):
                            score = cat_data.get('score', 0)
                            max_poss = cat_data.get('max_possible', 100)
                            category_totals[api_category] += score
                            if category_max_possible[api_category] == 0:
                                category_max_possible[api_category] = max_poss
                        else:
                            category_totals[api_category] += cat_data
                            if category_max_possible[api_category] == 0:
                                category_max_possible[api_category] = 100
                        
                        category_counts[api_category] += 1
        
        # Build response
        categories = []
        for api_category in category_mapping.values():
            count = category_counts.get(api_category, 0)
            total = category_totals.get(api_category, 0)
            max_poss = category_max_possible.get(api_category, 100)
            
            avg_score = round(total / count, 2) if count > 0 else 0
            percentage = round((total / (max_poss * count)) * 100, 2) if count > 0 and max_poss > 0 else 0
            
            categories.append({
                "category": api_category,
                "average_score": avg_score,
                "max_possible": max_poss,
                "percentage": percentage,
                "response_count": count
            })
        
        return {"categories": categories}
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@simple_admin_router.get("/nationality-breakdown")
async def get_nationality_breakdown(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    date_range: str = "30d",
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None)
):
    """Get nationality breakdown (Emirati vs Non-Emirati)."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile
        
        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )
        
        # Get all responses with filters applied
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply demographic filters
        query = apply_demographic_filters(query, filters, db)
        
        responses = query.all()
        
        # Apply unique user filter only if requested
        if unique_users_only:
            responses = filter_unique_users(responses)
        unique_responses = responses
        
        emirati_scores = []
        non_emirati_scores = []
        
        for response in unique_responses:
            if response.profile.nationality == "Emirati":
                emirati_scores.append(response.total_score)
            else:
                non_emirati_scores.append(response.total_score)
        
        return {
            "emirati": {
                "count": len(emirati_scores),
                "avg_score": round(sum(emirati_scores) / len(emirati_scores), 2) if emirati_scores else 0
            },
            "non_emirati": {
                "count": len(non_emirati_scores),
                "avg_score": round(sum(non_emirati_scores) / len(non_emirati_scores), 2) if non_emirati_scores else 0
            }
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@simple_admin_router.get("/age-breakdown")
async def get_age_breakdown(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    date_range: str = "30d",
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None)
):
    """Get age breakdown."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile
        
        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )
        
        # Get all responses with filters applied
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply demographic filters
        query = apply_demographic_filters(query, filters, db)
        
        responses = query.all()
        
        # Apply unique user filter only if requested
        if unique_users_only:
            responses = filter_unique_users(responses)
        unique_responses = responses
        
        # Calculate age groups
        age_group_data = {}
        
        for response in unique_responses:
            profile = response.profile
            if profile.date_of_birth:
                try:
                    parts = profile.date_of_birth.strip().split('/')
                    if len(parts) == 3:
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                        try:
                            birth_date = datetime(year, month, day)
                        except ValueError:
                            birth_date = datetime(year, 1, 1)
                        
                        today = datetime.now()
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        
                        # Categorize into age groups
                        if age < 25:
                            age_group = "18-24"
                        elif age < 35:
                            age_group = "25-34"
                        elif age < 45:
                            age_group = "35-44"
                        elif age < 55:
                            age_group = "45-54"
                        elif age < 65:
                            age_group = "55-64"
                        else:
                            age_group = "65+"
                        
                        if age_group not in age_group_data:
                            age_group_data[age_group] = {"scores": [], "count": 0}
                        
                        age_group_data[age_group]["scores"].append(response.total_score)
                        age_group_data[age_group]["count"] += 1
                except:
                    pass
        
        # Format response
        age_groups = []
        for age_group, data in age_group_data.items():
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            age_groups.append({
                "age_group": age_group,
                "count": data["count"],
                "avg_score": round(avg_score, 2)
            })
        
        # Sort by age group
        age_order = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        age_groups.sort(key=lambda x: age_order.index(x["age_group"]) if x["age_group"] in age_order else 999)
        
        return {
            "age_groups": age_groups,
            "total": sum(data["count"] for data in age_group_data.values())
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@simple_admin_router.get("/time-series")
async def get_time_series(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    date_range: str = "30d",
    group_by: str = "day",
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None)
):
    """Get time series data (submissions over time)."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile
        
        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )
        
        # Get all responses with filters applied
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply demographic filters
        query = apply_demographic_filters(query, filters, db)
        
        responses = query.all()
        
        # Apply unique user filter only if requested
        if unique_users_only:
            responses = filter_unique_users(responses)
        unique_responses = responses
        
        # Group by period
        time_data = {}
        
        for response in unique_responses:
            if response.created_at:
                if group_by == "day":
                    period = response.created_at.strftime("%Y-%m-%d")
                elif group_by == "week":
                    period = response.created_at.strftime("%Y-W%W")
                elif group_by == "month":
                    period = response.created_at.strftime("%Y-%m")
                else:
                    period = response.created_at.strftime("%Y")
                
                if period not in time_data:
                    time_data[period] = {"count": 0, "scores": []}
                
                time_data[period]["count"] += 1
                time_data[period]["scores"].append(response.total_score)
        
        # Format response
        time_series = []
        for period, data in sorted(time_data.items()):
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            time_series.append({
                "period": period,
                "count": data["count"],
                "avg_score": round(avg_score, 2)
            })
        
        return {"time_series": time_series}
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@simple_admin_router.get("/companies-analytics")
async def get_companies_analytics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    date_range: str = "30d",
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None)
):
    """Get companies analytics."""
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile, CompanyTracker
        
        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )
        
        # Get all responses with filters applied
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply demographic filters
        query = apply_demographic_filters(query, filters, db)
        
        responses = query.all()
        
        # Apply unique user filter only if requested
        if unique_users_only:
            responses = filter_unique_users(responses)
        unique_responses = responses
        
        # Group by company
        company_data = {}
        
        for response in unique_responses:
            if response.company_tracker_id:
                company_id = response.company_tracker_id
                
                if company_id not in company_data:
                    company = db.query(CompanyTracker).filter(CompanyTracker.id == company_id).first()
                    company_data[company_id] = {
                        "company_name": company.company_name if company else f"Company {company_id}",
                        "scores": [],
                        "status_bands": []
                    }
                
                company_data[company_id]["scores"].append(response.total_score)
                company_data[company_id]["status_bands"].append(response.status_band)
        
        # Format response
        companies = []
        for company_id, data in company_data.items():
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            
            # Count by status band
            excellent_count = data["status_bands"].count("Excellent")
            good_count = data["status_bands"].count("Good")
            needs_improvement_count = data["status_bands"].count("Needs Improvement")
            at_risk_count = data["status_bands"].count("At Risk")
            
            companies.append({
                "company_name": data["company_name"],
                "total_responses": len(data["scores"]),
                "avg_score": round(avg_score, 2),
                "excellent_count": excellent_count,
                "good_count": good_count,
                "needs_improvement_count": needs_improvement_count,
                "at_risk_count": at_risk_count
            })
        
        return {"companies": companies}
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@simple_admin_router.get("/score-analytics-table")
async def get_score_analytics_table(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
    date_range: str = "30d",
    age_groups: Optional[str] = Query(None),
    genders: Optional[str] = Query(None),
    nationalities: Optional[str] = Query(None),
    emirates: Optional[str] = Query(None),
    employment_statuses: Optional[str] = Query(None),
    income_ranges: Optional[str] = Query(None),
    children: Optional[str] = Query(None),
    companies: Optional[str] = Query(None),
    unique_users_only: Optional[bool] = Query(None)
):
    """Get score analytics table (question-level breakdown by nationality).
    
    If a company filter is applied, this will show questions from that company's
    variation set. Otherwise, it shows the default Financial Clinic questions.
    """
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile, VariationSet, QuestionVariation
        from app.surveys.financial_clinic_questions import FINANCIAL_CLINIC_QUESTIONS
        
        # Parse filters
        filters = parse_filter_params(
            age_groups, genders, nationalities, emirates,
            employment_statuses, income_ranges, children, companies
        )
        
        # Get all responses with filters applied
        query = db.query(FinancialClinicResponse).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply demographic filters
        query = apply_demographic_filters(query, filters, db)
        
        responses = query.all()
        
        # Apply unique user filter only if requested
        if unique_users_only:
            responses = filter_unique_users(responses)
        unique_responses = responses
        
        # Determine which questions to analyze based on company filter
        questions_to_analyze = FINANCIAL_CLINIC_QUESTIONS  # Default
        company_variation_set_name = None
        
        # If company filter is applied, get the company's variation set questions
        if filters.get('companies') and len(filters['companies']) == 1:
            company_identifier = filters['companies'][0]
            
            # Get company and its variation set
            company = db.query(CompanyTracker).filter(
                or_(
                    CompanyTracker.company_name == company_identifier,
                    CompanyTracker.unique_url == company_identifier
                )
            ).first()
            
            if company and company.variation_set_id:
                # Get the variation set
                variation_set = db.query(VariationSet).filter(
                    VariationSet.id == company.variation_set_id
                ).first()
                
                if variation_set:
                    company_variation_set_name = variation_set.name
                    # Get all 15 question variations from the set
                    variation_ids = [
                        variation_set.q1_variation_id, variation_set.q2_variation_id,
                        variation_set.q3_variation_id, variation_set.q4_variation_id,
                        variation_set.q5_variation_id, variation_set.q6_variation_id,
                        variation_set.q7_variation_id, variation_set.q8_variation_id,
                        variation_set.q9_variation_id, variation_set.q10_variation_id,
                        variation_set.q11_variation_id, variation_set.q12_variation_id,
                        variation_set.q13_variation_id, variation_set.q14_variation_id,
                        variation_set.q15_variation_id
                    ]
                    
                    # Get all variations
                    variations = db.query(QuestionVariation).filter(
                        QuestionVariation.id.in_(variation_ids),
                        QuestionVariation.is_active == True
                    ).all()
                    
                    if variations:
                        # Convert variations to question-like objects for analysis
                        questions_to_analyze = []
                        for i, var in enumerate(variations, start=1):
                            # Create a simple object with the needed attributes
                            class VariationQuestion:
                                def __init__(self, variation, question_number):
                                    self.id = variation.base_question_id
                                    self.number = question_number
                                    self.text_en = variation.text_en or variation.text  # Use bilingual field or fallback
                                    self.category = type('obj', (object,), {
                                        'value': variation.factor or "General"  # Use factor as category
                                    })()
                            
                            questions_to_analyze.append(VariationQuestion(var, i))
        
        # Build question analytics with nationality breakdown
        question_analytics = []
        
        for question in questions_to_analyze:
            question_id = question.id
            question_number = question.number
            question_text = question.text_en
            category = question.category.value  # Get the string value like "Income Stream"
            
            # Collect scores by nationality
            emirati_scores = []
            non_emirati_scores = []
            
            for response in unique_responses:
                # Get profile
                profile = db.query(FinancialClinicProfile).filter(
                    FinancialClinicProfile.id == response.profile_id
                ).first()
                
                # Get answer for this question
                if response.answers and question_id in response.answers:
                    answer_value = response.answers[question_id]
                    
                    if profile:
                        if profile.nationality == "Emirati":
                            emirati_scores.append(answer_value)
                        else:
                            non_emirati_scores.append(answer_value)
            
            # Calculate averages
            emirati_avg = sum(emirati_scores) / len(emirati_scores) if emirati_scores else None
            non_emirati_avg = sum(non_emirati_scores) / len(non_emirati_scores) if non_emirati_scores else None
            
            question_analytics.append({
                "question_number": question_number,
                "question_text": question_text,
                "category": category,
                "emirati_avg": round(emirati_avg, 2) if emirati_avg is not None else None,
                "emirati_count": len(emirati_scores),
                "non_emirati_avg": round(non_emirati_avg, 2) if non_emirati_avg is not None else None,
                "non_emirati_count": len(non_emirati_scores)
            })
        
        # Return with metadata about which question set is being used
        return {
            "questions": question_analytics,
            "total_questions": len(question_analytics),
            "question_set_type": "company_variation" if company_variation_set_name else "default",
            "variation_set_name": company_variation_set_name,
            "filtered": bool(filters.get('companies'))
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "questions": [],
            "total_questions": 0
        }

@simple_admin_router.get("/submissions")
async def get_submissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_band: Optional[str] = None,
    nationality: Optional[str] = None,
    company_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of all Financial Clinic submissions with filtering.
    """
    try:
        from app.models import FinancialClinicResponse, FinancialClinicProfile
        
        # Build query with joins
        query = db.query(
            FinancialClinicResponse,
            FinancialClinicProfile
        ).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    FinancialClinicProfile.name.ilike(search_term),
                    FinancialClinicProfile.email.ilike(search_term),
                    FinancialClinicProfile.mobile_number.ilike(search_term)
                )
            )
        
        if status_band:
            query = query.filter(FinancialClinicResponse.status_band == status_band)
        
        if nationality:
            query = query.filter(FinancialClinicProfile.nationality == nationality)
        
        if company_id:
            query = query.filter(FinancialClinicResponse.company_tracker_id == company_id)
        
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
            query = query.filter(FinancialClinicResponse.created_at >= date_from_dt)
        
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to)
            query = query.filter(FinancialClinicResponse.created_at <= date_to_dt)
        
        # Get total count
        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        # Get paginated results
        offset = (page - 1) * page_size
        results = query.order_by(
            FinancialClinicResponse.created_at.desc()
        ).offset(offset).limit(page_size).all()
        
        # Helper function to calculate age from DOB string (DD/MM/YYYY)
        def calculate_age(dob_str):
            try:
                dob = datetime.strptime(dob_str, '%d/%m/%Y')
                today = datetime.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                return age
            except:
                return None
        
        # Format submissions
        submissions = []
        for response, profile in results:
            # Get company name if exists
            company_name = None
            if response.company_tracker_id:
                company = db.query(CompanyTracker).filter(
                    CompanyTracker.id == response.company_tracker_id
                ).first()
                if company:
                    company_name = company.company_name
            
            submissions.append({
                'id': response.id,
                'profile_id': profile.id,
                'profile_name': profile.name,
                'profile_email': profile.email,
                'profile_mobile': profile.mobile_number,
                'gender': profile.gender,
                'nationality': profile.nationality,
                'emirate': profile.emirate,
                'age': calculate_age(profile.date_of_birth) if profile.date_of_birth else None,
                'employment_status': profile.employment_status,
                'income_range': profile.income_range,
                'company_name': company_name,
                'total_score': round(response.total_score, 2),
                'status_band': response.status_band,
                'questions_answered': response.questions_answered,
                'total_questions': response.total_questions,
                'category_scores': response.category_scores,
                'created_at': response.created_at.isoformat(),
                'completed_at': response.completed_at.isoformat() if response.completed_at else None,
            })
        
        return {
            'submissions': submissions,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }
        
    except Exception as e:
        import traceback
        print(f"Error in get_submissions: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@simple_admin_router.get("/submissions/stats")
async def get_submissions_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about Financial Clinic submissions.
    """
    try:
        from app.models import FinancialClinicResponse
        
        # Total submissions
        total = db.query(FinancialClinicResponse).count()
        
        # Today's submissions
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today = db.query(FinancialClinicResponse).filter(
            FinancialClinicResponse.created_at >= today_start
        ).count()
        
        # This week's submissions
        week_start = today_start - timedelta(days=today_start.weekday())
        this_week = db.query(FinancialClinicResponse).filter(
            FinancialClinicResponse.created_at >= week_start
        ).count()
        
        # This month's submissions
        month_start = today_start.replace(day=1)
        this_month = db.query(FinancialClinicResponse).filter(
            FinancialClinicResponse.created_at >= month_start
        ).count()
        
        # Average score
        avg_score_result = db.query(
            func.avg(FinancialClinicResponse.total_score)
        ).scalar()
        average_score = float(avg_score_result) if avg_score_result else 0.0
        
        return {
            'total': total,
            'today': today,
            'this_week': this_week,
            'this_month': this_month,
            'average_score': round(average_score, 2)
        }
        
    except Exception as e:
        import traceback
        print(f"Error in get_submissions_stats: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@simple_admin_router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a Financial Clinic submission by ID.
    """
    try:
        from app.models import FinancialClinicResponse
        
        # Find the submission
        submission = db.query(FinancialClinicResponse).filter(
            FinancialClinicResponse.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Delete the submission
        db.delete(submission)
        db.commit()
        
        return {
            'success': True,
            'message': 'Submission deleted successfully',
            'id': submission_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in delete_submission: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))