"""
Financial Clinic API Routes

Endpoints for the Financial Clinic survey system:
- POST /financial-clinic/calculate - Calculate score and get results
- GET /financial-clinic/questions - Get question set
- POST /financial-clinic/submit - Submit survey and save results
- GET /financial-clinic/history - Get user's assessment history
- GET /financial-clinic/{response_id} - Get specific assessment
- POST /financial-clinic/report/pdf - Generate PDF report
- POST /financial-clinic/report/email - Send email report
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import logging
import io
from datetime import datetime

from ..database import get_db
from ..models import User, CustomerProfile, SurveyResponse, Product
from ..auth.dependencies import get_current_user, get_current_admin_user
from .financial_clinic_questions import get_questions_for_profile, FINANCIAL_CLINIC_QUESTIONS
from .financial_clinic_scoring import calculate_financial_clinic_score, FinancialClinicScorer
from .financial_clinic_insights import generate_insights
from .financial_clinic_products import get_product_recommendations

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financial-clinic", tags=["Financial Clinic"])


# ==================== Helper Functions ====================

def convert_age_to_dob(age: int) -> str:
    """
    Convert age to approximate date of birth in DD/MM/YYYY format.
    Uses January 1st of the calculated birth year.
    
    Args:
        age: Age in years
        
    Returns:
        Date of birth string in DD/MM/YYYY format
    """
    current_year = datetime.now().year
    birth_year = current_year - age
    return f"01/01/{birth_year}"


# ==================== Request/Response Models ====================

class FinancialClinicAnswers(BaseModel):
    """Survey answers submission."""
    responses: Dict[str, int]  # question_id -> answer_value (1-5)
    has_children: bool = False


class ProfileData(BaseModel):
    """Customer profile data for recommendations."""
    # Required fields (but flexible for resumed surveys)
    name: str = ""
    date_of_birth: str = ""  # Format: DD/MM/YYYY
    age: Optional[int] = None  # Alternative to date_of_birth (will be converted)
    gender: str = ""  # Male, Female
    nationality: str = ""  # Emirati, Non-Emirati
    children: int = 0  # 0-5+
    employment_status: str = ""  # Employed, Self-Employed, Unemployed
    income_range: str = ""  # Below 5K, 5K-10K, etc.
    emirate: str = ""  # Dubai, Abu Dhabi, Sharjah, etc.
    email: str  # This is truly required
    
    # Optional fields
    mobile_number: Optional[str] = None


class FinancialClinicCalculateRequest(BaseModel):
    """Request for score calculation."""
    answers: Dict[str, int]
    profile: ProfileData
    company_url: Optional[str] = None  # Company unique URL for tracking


class QuestionResponse(BaseModel):
    """Question for frontend display."""
    id: str
    number: int
    category: str
    weight: int
    text_en: str
    text_ar: str
    options: List[Dict]
    conditional: bool


class FinancialClinicResultResponse(BaseModel):
    """Complete Financial Clinic result."""
    total_score: float
    status_band: str
    category_scores: Dict
    insights: List[Dict]
    products: List[Dict]
    questions_answered: int
    total_questions: int


# ==================== API Endpoints ====================

@router.get("/questions", response_model=List[QuestionResponse])
async def get_financial_clinic_questions(
    children: int = 0,
    language: str = "en",
    company_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get Financial Clinic questions based on profile and optional company variations.
    
    Args:
        children: Number of children (0 = no children, >= 1 = has children)
        language: "en" or "ar"
        company_url: Optional company unique URL for custom question variations
        
    Returns:
        14 or 15 questions depending on children count:
        - If children = 0: Returns 14 questions (Q15 excluded)
        - If children > 0: Returns all 15 questions (Q15 included)
        - If company_url provided: Questions may include custom variations
    """
    # Get base questions
    questions = get_questions_for_profile(children_count=children)
    
    # If company URL provided, check for variations (only if explicitly enabled)
    if company_url:
        from ..models import CompanyTracker, QuestionVariation, VariationSet
        from .financial_clinic_questions import FinancialClinicQuestion, FinancialClinicOption
        
        company = db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == company_url,
            CompanyTracker.is_active == True
        ).first()
        
        # Only apply variations if explicitly enabled
        if company and company.enable_variations:
            # Priority 1: Check for assigned variation set
            if company.variation_set_id:
                variation_set = db.query(VariationSet).filter(
                    VariationSet.id == company.variation_set_id,
                    VariationSet.is_active == True
                ).first()
                
                if variation_set:
                    # Use variations from set
                    variation_mapping = {
                        'fc_q1': variation_set.q1_variation_id,
                        'fc_q2': variation_set.q2_variation_id,
                        'fc_q3': variation_set.q3_variation_id,
                        'fc_q4': variation_set.q4_variation_id,
                        'fc_q5': variation_set.q5_variation_id,
                        'fc_q6': variation_set.q6_variation_id,
                        'fc_q7': variation_set.q7_variation_id,
                        'fc_q8': variation_set.q8_variation_id,
                        'fc_q9': variation_set.q9_variation_id,
                        'fc_q10': variation_set.q10_variation_id,
                        'fc_q11': variation_set.q11_variation_id,
                        'fc_q12': variation_set.q12_variation_id,
                        'fc_q13': variation_set.q13_variation_id,
                        'fc_q14': variation_set.q14_variation_id,
                        'fc_q15': variation_set.q15_variation_id,
                    }
                    
                    # Replace questions with variations from set
                    for base_q_id, variation_id in variation_mapping.items():
                        variation = db.query(QuestionVariation).filter(
                            QuestionVariation.id == variation_id,
                            QuestionVariation.is_active == True
                        ).first()
                        
                        if variation:
                            # Find and replace the question
                            for i, q in enumerate(questions):
                                if q.id == base_q_id:
                                    # Use bilingual fields (text_en, text_ar)
                                    questions[i] = FinancialClinicQuestion(
                                        id=q.id,  # Keep same ID for scoring
                                        number=q.number,
                                        category=q.category,
                                        weight=q.weight,
                                        text_en=variation.text_en or variation.text,
                                        text_ar=variation.text_ar or variation.text,
                                        options=[
                                            FinancialClinicOption(
                                                value=opt['value'],
                                                label_en=opt.get('label_en', opt.get('label', f"[Option {opt['value']}]")),
                                                label_ar=opt.get('label_ar', opt.get('label', f"[خيار {opt['value']}]"))
                                            )
                                            for opt in variation.options
                                        ],
                                        conditional=q.conditional,
                                        condition_field=q.condition_field,
                                        condition_value=q.condition_value
                                    )
            
            # Priority 2: Fall back to individual question_variation_mapping (legacy)
            elif company and company.question_variation_mapping:
                # Replace questions with variations
                for base_q_id, variation_id in company.question_variation_mapping.items():
                    variation = db.query(QuestionVariation).filter(
                        QuestionVariation.id == variation_id,
                        QuestionVariation.is_active == True
                    ).first()
                    
                    if variation:
                        # Find and replace the question
                        for i, q in enumerate(questions):
                            if q.id == base_q_id:
                                # Replace with variation text/options (use bilingual fields)
                                questions[i] = FinancialClinicQuestion(
                                    id=q.id,  # Keep same ID for scoring
                                    number=q.number,
                                    category=q.category,
                                    weight=q.weight,
                                    text_en=variation.text_en or variation.text,
                                    text_ar=variation.text_ar or variation.text,
                                    options=[
                                        FinancialClinicOption(
                                            value=opt['value'],
                                            label_en=opt.get('label_en', opt.get('label', f"[Option {opt['value']}]")),
                                            label_ar=opt.get('label_ar', opt.get('label', f"[خيار {opt['value']}]"))
                                        )
                                        for opt in variation.options
                                    ],
                                    conditional=q.conditional,
                                    condition_field=q.condition_field,
                                    condition_value=q.condition_value
                                )
    
    return [
        {
            "id": q.id,
            "number": q.number,
            "category": q.category.value,
            "weight": q.weight,
            "text_en": q.text_en,
            "text_ar": q.text_ar,
            "options": [
                {
                    "value": opt.value,
                    "label_en": opt.label_en,
                    "label_ar": opt.label_ar
                }
                for opt in q.options
            ],
            "conditional": q.conditional
        }
        for q in questions
    ]


@router.post("/calculate", response_model=FinancialClinicResultResponse)
async def calculate_financial_clinic_result(
    request: FinancialClinicCalculateRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate Financial Clinic score, insights, and product recommendations.
    
    This endpoint:
    1. Validates responses
    2. Calculates 0-100 score with category breakdown
    3. Generates personalized insights (max 5)
    4. Recommends products (max 3) based on demographics
    
    Args:
        request: Survey answers and profile data
        
    Returns:
        Complete results with score, insights, and products
    """
    # Get children count from profile
    children_count = request.profile.children
    
    # Validate responses count based on children status
    expected_count = 15 if children_count > 0 else 14
    if len(request.answers) != expected_count:
        raise HTTPException(
            status_code=400,
            detail=f"Must provide responses for {expected_count} questions. Received {len(request.answers)} responses."
        )
    
    scorer = FinancialClinicScorer()
    is_valid, errors = scorer.validate_responses(request.answers)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Calculate score with children count for conditional Q15 logic
    score_result = calculate_financial_clinic_score(
        responses=request.answers,
        children_count=children_count
    )
    
    # Generate insights with profile data for conditional logic
    insights = generate_insights(
        category_scores=score_result["category_scores"],
        profile={
            'income_range': request.profile.income_range,
            'nationality': request.profile.nationality,
            'gender': request.profile.gender,
            'children': request.profile.children
        },
        max_insights=5
    )
    
    # Get product recommendations
    products = get_product_recommendations(
        db=db,
        category_scores=score_result["category_scores"],
        nationality=request.profile.nationality,
        gender=request.profile.gender,
        children=request.profile.children
    )
    
    return {
        "total_score": score_result["total_score"],
        "status_band": score_result["status_band"],
        "category_scores": score_result["category_scores"],
        "insights": insights,
        "products": products,
        "questions_answered": score_result["questions_answered"],
        "total_questions": score_result["total_questions"]
    }


@router.post("/submit")
async def submit_financial_clinic_survey(
    request: FinancialClinicCalculateRequest,
    db: Session = Depends(get_db)
    # TODO: Add authentication: current_user: User = Depends(get_current_user)
):
    """
    Submit Financial Clinic survey and save to database.
    
    This endpoint:
    1. Calculates results (same as /calculate)
    2. Saves survey response to database
    3. Returns complete results with survey_response_id
    
    Args:
        request: Survey answers and profile data
        
    Returns:
        Saved survey response with ID
    """
    from app.models import FinancialClinicProfile, FinancialClinicResponse
    from datetime import datetime
    
    try:
        logger.info(f"📝 Survey submission started")
        logger.info(f"📝 Answers count: {len(request.answers) if request.answers else 0}")
        logger.info(f"📝 Profile email: {request.profile.email if request.profile else 'None'}")
        logger.info(f"📝 Company URL: {request.company_url}")
        
        # Validate required data
        if not request.answers:
            raise HTTPException(status_code=422, detail="No answers provided")
        if not request.profile:
            raise HTTPException(status_code=422, detail="No profile data provided")
        if not request.profile.email:
            raise HTTPException(status_code=422, detail="Email is required in profile")
            
    except Exception as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise
    
    # Calculate results first
    result = await calculate_financial_clinic_result(request, db)
    
    # Convert Pydantic model to dict
    result_dict = result.dict() if hasattr(result, 'dict') else result
    
    # Save to database
    try:
        # 1. Check for company tracking
        company_tracker_id = None
        if request.company_url:
            from app.models import CompanyTracker
            company = db.query(CompanyTracker).filter(
                CompanyTracker.unique_url == request.company_url,
                CompanyTracker.is_active == True
            ).first()
            if company:
                company_tracker_id = company.id
                logger.info(f"Survey linked to company: {company.company_name}")
        
        # 2. Create or get profile
        profile_data = request.profile.dict() if request.profile else {}
        logger.info(f"📝 Profile data received: {profile_data}")
        
        # Check if profile exists by email
        existing_profile = None
        if profile_data.get('email'):
            existing_profile = db.query(FinancialClinicProfile).filter(
                FinancialClinicProfile.email == profile_data['email']
            ).first()
        
        # Convert age to date_of_birth if age is provided but date_of_birth is not
        if 'age' in profile_data and profile_data['age'] and not profile_data.get('date_of_birth'):
            try:
                age = int(profile_data['age'])
                profile_data['date_of_birth'] = convert_age_to_dob(age)
                logger.info(f"🔄 Converted age {age} to date_of_birth: {profile_data['date_of_birth']}")
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Failed to convert age to date_of_birth: {e}")
                profile_data['date_of_birth'] = '01/01/1990'  # Fallback
        
        if existing_profile:
            # Update existing profile with non-empty values
            for key, value in profile_data.items():
                if hasattr(existing_profile, key) and value is not None and value != "":
                    setattr(existing_profile, key, value)
            profile = existing_profile
            logger.info(f"📝 Updated existing profile for: {existing_profile.email}")
        else:
            # Create new profile with flexible fields for resumed surveys
            profile = FinancialClinicProfile(
                name=profile_data.get('name', 'Anonymous User'),
                date_of_birth=profile_data.get('date_of_birth', '01/01/1990'),
                gender=profile_data.get('gender', 'Not Specified'),
                nationality=profile_data.get('nationality', 'Not Specified'),
                children=profile_data.get('children', 0),
                employment_status=profile_data.get('employment_status', 'Not Specified'),
                income_range=profile_data.get('income_range', 'Not Specified'),
                emirate=profile_data.get('emirate', 'Not Specified'),
                email=profile_data.get('email', ''),
                mobile_number=profile_data.get('mobile_number')
            )
            db.add(profile)
            logger.info(f"📝 Created new profile for: {profile.email}")
            db.flush()  # Get profile.id
        
        # 3. Create survey response
        survey_response = FinancialClinicResponse(
            profile_id=profile.id,
            company_tracker_id=company_tracker_id,
            answers=request.answers,
            total_score=result_dict['total_score'],
            status_band=result_dict['status_band'],
            category_scores=result_dict['category_scores'],
            insights=result_dict.get('insights', []),
            product_recommendations=result_dict.get('products', []),
            questions_answered=result_dict.get('questions_answered', len(request.answers)),
            total_questions=result_dict.get('total_questions', 15),
            completed_at=datetime.utcnow()  # Set completion timestamp
        )
        db.add(survey_response)
        db.commit()
        db.refresh(survey_response)
        
        # 4. Create CompanyAssessment record if linked to a company
        if company_tracker_id:
            from app.models import CompanyTracker, CompanyAssessment
            
            # Create a CompanyAssessment record
            company_assessment = CompanyAssessment(
                company_tracker_id=company_tracker_id,
                employee_id=None,  # Anonymous
                department=profile_data.get('department'),
                position_level=None,
                responses=request.answers,
                overall_score=result_dict['total_score'],
                category_scores=result_dict['category_scores']
            )
            db.add(company_assessment)
            db.commit()
            
            # Update company statistics
            company = db.query(CompanyTracker).filter(CompanyTracker.id == company_tracker_id).first()
            if company:
                # Recalculate company statistics
                total_assessments = db.query(FinancialClinicResponse).filter(
                    FinancialClinicResponse.company_tracker_id == company_tracker_id
                ).count()
                
                avg_score = db.query(func.avg(FinancialClinicResponse.total_score)).filter(
                    FinancialClinicResponse.company_tracker_id == company_tracker_id
                ).scalar()
                
                company.total_assessments = total_assessments
                company.average_score = float(avg_score) if avg_score else None
                db.commit()
                logger.info(f"Updated company stats: {total_assessments} assessments, avg score: {avg_score}")
        
        # 5. Return results with survey_response_id
        return {
            **result_dict,
            "survey_response_id": survey_response.id,
            "saved_at": survey_response.created_at.isoformat() if survey_response.created_at else None,
            "company_tracked": company_tracker_id is not None
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving Financial Clinic survey: {e}")
        # Return results anyway, just without saving
        return {
            **result_dict,
            "survey_response_id": None,
            "saved_at": None,
            "save_error": str(e)
        }


@router.get("/stats")
async def get_financial_clinic_stats(db: Session = Depends(get_db)):
    """
    Get Financial Clinic statistics.
    
    Returns:
        Statistics about surveys completed, average scores, etc.
    """
    # Count surveys by version
    v2_count = db.query(SurveyResponse).filter(
        SurveyResponse.survey_version == 'v2'
    ).count()
    
    return {
        "total_financial_clinic_surveys": v2_count,
        "active_products": db.query(Product).filter(Product.active == True).count()
    }


class PDFReportRequest(BaseModel):
    """Request for PDF report generation."""
    survey_response_id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None  # Changed from FinancialClinicResultResponse for flexibility
    profile: Optional[Dict[str, Any]] = None  # Changed from ProfileData for flexibility
    language: str = "en"


class EmailReportRequest(BaseModel):
    """Request for email report."""
    survey_response_id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None  # Changed from FinancialClinicResultResponse for flexibility
    profile: Optional[Dict[str, Any]] = None  # Changed from ProfileData for flexibility
    email: str
    language: str = "en"


# ==================== Helper Functions ====================

def convert_response_to_survey_data(response):
    """Convert FinancialClinicResponse to survey_data format for PDF/Email."""
    # Calculate status_level from status_band
    status_level_map = {
        'At Risk': 1,
        'Needs Improvement': 2,
        'Moderate': 3,
        'Good': 4,
        'Excellent': 5
    }
    status_level = status_level_map.get(response.status_band, 3)
    
    # Serialize profile properly (exclude SQLAlchemy internal keys)
    profile_data = {}
    if response.profile:
        for key in ['name', 'date_of_birth', 'gender', 'nationality', 'children', 
                   'employment_status', 'income_range', 'emirate', 'email', 'mobile_number']:
            if hasattr(response.profile, key):
                profile_data[key] = getattr(response.profile, key)
    
    # Convert category_scores dict to list format for email template
    category_scores_list = []
    if response.category_scores:
        for cat_name, cat_data in response.category_scores.items():
            category_scores_list.append({
                'category': cat_name,
                'category_ar': cat_name,  # TODO: Add Arabic translations
                'score': cat_data.get('score', 0),
                'max_possible': cat_data.get('max_possible', 0),
                'percentage': cat_data.get('percentage', 0),
                'status_level': cat_data.get('status_level', 'moderate')
            })
    
    return {
        'profile': profile_data,
        'result': {
            'total_score': response.total_score,
            'status_band': response.status_band,
            'status_level': status_level,
            'category_scores': category_scores_list,
            'insights': response.insights,
            'products': response.product_recommendations,
        }
    }


# ==================== PDF & Email Routes ====================

@router.post("/report/pdf")
async def generate_pdf_report(
    request: PDFReportRequest,
    db: Session = Depends(get_db)
):
    """
    Generate PDF report for Financial Clinic results using existing report service.
    
    Can work with either:
    - survey_response_id: Fetch saved results from database
    - result + profile: Generate from provided data
    
    Args:
        request: PDF generation request
        
    Returns:
        PDF file download
    """
    try:
        from app.reports.report_generation_service import ReportGenerationService
        from app.models import FinancialClinicResponse
        
        service = ReportGenerationService()
        
        # Check if the specific method exists
        if not hasattr(service, 'generate_financial_clinic_pdf'):
            # Fallback: Return a simple message PDF using generic method
            return {
                "success": False,
                "message": "PDF generation for Financial Clinic is being configured",
                "note": "The Financial Clinic PDF template needs to be added to the report service."
            }
        
        # If survey_response_id provided, load from database
        if request.survey_response_id:
            response = db.query(FinancialClinicResponse).filter(
                FinancialClinicResponse.id == request.survey_response_id
            ).first()
            
            if not response:
                raise HTTPException(status_code=404, detail="Survey response not found")
            
            # Use helper function to convert response to survey_data format
            survey_data = convert_response_to_survey_data(response)
        elif request.result:
            # Use provided result data
            # Handle result - could be dict or Pydantic model
            if isinstance(request.result, dict):
                result_data = request.result
            elif hasattr(request.result, 'dict'):
                result_data = request.result.dict()
            else:
                result_data = request.result
            
            # Handle profile - could be dict or Pydantic model
            if request.profile:
                if isinstance(request.profile, dict):
                    profile_data = request.profile
                elif hasattr(request.profile, 'dict'):
                    profile_data = request.profile.dict()
                else:
                    profile_data = request.profile
            else:
                profile_data = {}
            
            survey_data = {
                'profile': profile_data,
                'result': result_data
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Either survey_response_id or result must be provided"
            )
        
        # Generate PDF using existing service
        logger.info(f"Generating PDF with survey_data keys: {survey_data.keys()}")
        logger.info(f"Language: {request.language}")
        pdf_content = await service.generate_financial_clinic_pdf(
            survey_data=survey_data,
            language=request.language
        )
        logger.info(f"PDF generated successfully, size: {len(pdf_content)} bytes")
        
        # Generate filename with current date
        filename = f"financial-clinic-report-{datetime.now().strftime('%Y-%m-%d')}.pdf"
        
        # Return PDF
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except AttributeError as e:
        # Method doesn't exist yet
        return {
            "success": False,
            "message": "PDF generation for Financial Clinic is being configured",
            "note": "The Financial Clinic PDF template needs to be added to the report service.",
            "technical_detail": str(e) if True else None  # Show in debug mode
        }
    except ImportError:
        # If report service is not available, return placeholder
        return {
            "success": False,
            "message": "PDF generation service not configured",
            "note": "Please check report services configuration."
        }
    except Exception as e:
        # Return informative error instead of 500
        return {
            "success": False,
            "message": "PDF generation encountered an error",
            "error": str(e)
        }


def import_current_date():
    """Helper to get current date."""
    from datetime import datetime
    return datetime.now().strftime("%B %d, %Y")


@router.post("/report/email")
async def send_email_report(
    request: EmailReportRequest,
    db: Session = Depends(get_db)
):
    """
    Send email report with Financial Clinic results using existing email service.
    
    Args:
        request: Email report request
        
    Returns:
        Confirmation of email sent
    """
    try:
        from app.reports.email_service import EmailReportService
        from app.reports.report_generation_service import ReportGenerationService
        from app.models import FinancialClinicResponse
        import re
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, request.email):
            raise HTTPException(status_code=400, detail="Invalid email address")
        
        email_service = EmailReportService()
        report_service = ReportGenerationService()
        
        # Check if email service has Financial Clinic method
        if not hasattr(email_service, 'send_financial_clinic_report'):
            # Return graceful message
            return {
                "success": False,
                "message": f"Email will be sent to {request.email} once service is configured",
                "email": request.email,
                "note": "The Financial Clinic email template needs to be added to the email service."
            }
        
        # Prepare survey data
        if request.survey_response_id:
            response = db.query(FinancialClinicResponse).filter(
                FinancialClinicResponse.id == request.survey_response_id
            ).first()
            
            if not response:
                raise HTTPException(status_code=404, detail="Survey response not found")
            
            # Use helper function to convert response to survey_data format
            survey_data = convert_response_to_survey_data(response)
        elif request.result:
            # Use provided result data  
            logger.info(f"📧 EMAIL - request.result type: {type(request.result)}")
            
            # Handle result - could be dict, string (JSON), or Pydantic model
            if isinstance(request.result, str):
                import json
                try:
                    result_data = json.loads(request.result)
                    logger.info("📧 Parsed result from JSON string")
                except Exception as e:
                    logger.error(f"📧 Failed to parse result JSON: {e}")
                    result_data = {}
            elif isinstance(request.result, dict):
                result_data = request.result
                logger.info("📧 Using result as dict directly")
            else:
                logger.warning(f"📧 Unexpected result type: {type(request.result)}")
                result_data = {}
            
            # Handle profile
            if request.profile:
                if isinstance(request.profile, str):
                    import json
                    try:
                        profile_data = json.loads(request.profile)
                    except:
                        profile_data = {}
                elif isinstance(request.profile, dict):
                    profile_data = request.profile
                else:
                    profile_data = {}
            else:
                profile_data = {}
            
            survey_data = {
                'profile': profile_data,
                'result': result_data
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Either survey_response_id or result must be provided"
            )
        
        # Strip whitespace and normalize language parameter (critical fix for production)
        language = request.language.strip().lower() if request.language else "en"
        
        # Log language for debugging
        logger.info(f"📧 EMAIL - Language parameter: '{request.language}' -> '{language}' (type: {type(language)})")
        logger.info(f"📧 EMAIL - Is Arabic: {language == 'ar'}")
        
        # Generate PDF only for English (Arabic PDF has layout issues)
        pdf_content = None
        if language != 'ar':
            try:
                pdf_content = await report_service.generate_financial_clinic_pdf(
                    survey_data=survey_data,
                    language=language
                )
                logger.info(f"✅ PDF generated successfully for language: {language}")
            except Exception as e:
                logger.error(f"❌ PDF generation failed: {e}")
                # Continue without PDF
                pdf_content = None
        else:
            logger.info(f"⏭️ Skipping PDF generation for Arabic language")
        
        # Send email with or without PDF attachment
        email_result = await email_service.send_financial_clinic_report(
            recipient_email=request.email,
            result=survey_data['result'],
            pdf_content=pdf_content,
            profile=survey_data['profile'],
            language=language
        )
        
        if email_result.get('success'):
            return {
                "success": True,
                "message": f"Report sent to {request.email}",
                "email": request.email
            }
        else:
            return {
                "success": False,
                "message": email_result.get('message', f"Failed to send email to {request.email}"),
                "email": request.email,
                "error": email_result.get('error')
            }
        
    except AttributeError:
        # Method doesn't exist yet
        return {
            "success": False,
            "message": f"Email will be sent to {request.email} once service is configured",
            "email": request.email,
            "note": "The Financial Clinic email template needs to be added to the email service."
        }
    except ImportError:
        # Email service not configured
        return {
            "success": False,
            "message": f"Email will be sent to {request.email}",
            "email": request.email,
            "note": "Email functionality not yet configured. Configure SMTP settings to enable."
        }
    except Exception as e:
        # Return informative error
        return {
            "success": False,
            "message": "Email sending encountered an error",
            "email": request.email,
            "error": str(e)
        }


@router.get("/history")
async def get_financial_clinic_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's Financial Clinic assessment history.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of user's Financial Clinic assessments
    """
    from app.models import FinancialClinicResponse, FinancialClinicProfile
    
    # Query responses by joining through profile and matching user's email
    responses = db.query(FinancialClinicResponse).join(
        FinancialClinicProfile,
        FinancialClinicResponse.profile_id == FinancialClinicProfile.id
    ).filter(
        FinancialClinicProfile.email == current_user.email
    ).order_by(FinancialClinicResponse.created_at.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": r.id,
        "total_score": r.total_score,
        "status_band": r.status_band,
        "status_level": getattr(r, 'status_level', 0),  # Use getattr with default
        "created_at": r.created_at.isoformat(),
        "category_scores": r.category_scores,
        "questions_answered": r.questions_answered
    } for r in responses]


@router.get("/{response_id}")
async def get_financial_clinic_result(
    response_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific Financial Clinic assessment result.
    
    Args:
        response_id: ID of the survey response
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Complete assessment result with all details
    """
    from app.models import FinancialClinicResponse
    
    response = db.query(FinancialClinicResponse).filter(
        FinancialClinicResponse.id == response_id,
        FinancialClinicResponse.user_id == current_user.id
    ).first()
    
    if not response:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return {
        "id": response.id,
        "total_score": response.total_score,
        "status_band": response.status_band,
        "status_level": response.status_level,
        "category_scores": response.category_scores,
        "insights": response.insights,
        "products": response.recommended_products,
        "questions_answered": response.questions_answered,
        "total_questions": response.total_questions,
        "created_at": response.created_at.isoformat(),
        "profile": {
            "name": response.profile.name,
            "date_of_birth": response.profile.date_of_birth,
            "gender": response.profile.gender,
            "nationality": response.profile.nationality,
            "children": response.profile.children,
            "employment_status": response.profile.employment_status,
            "income_range": response.profile.income_range,
            "emirate": response.profile.emirate,
            "email": response.profile.email
        } if response.profile else None
    }


# ==================== Company Analytics Endpoints ====================

@router.get("/company/{company_url}/analytics")
async def get_company_financial_clinic_analytics(
    company_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get Financial Clinic analytics for a specific company.
    Admin only.
    
    Returns aggregated statistics, score distributions, and demographic breakdowns
    for all Financial Clinic assessments completed through the company's unique URL.
    """
    from app.models import CompanyTracker, FinancialClinicResponse, FinancialClinicProfile
    
    # Get company
    company = db.query(CompanyTracker).filter(
        CompanyTracker.unique_url == company_url
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get all responses for this company
    responses = db.query(FinancialClinicResponse).filter(
        FinancialClinicResponse.company_tracker_id == company.id
    ).all()
    
    if not responses:
        return {
            "company_name": company.company_name,
            "company_url": company_url,
            "total_assessments": 0,
            "average_score": None,
            "status_distribution": {},
            "category_averages": {},
            "demographic_breakdown": {}
        }
    
    # Calculate statistics
    total_assessments = len(responses)
    total_score = sum(r.total_score for r in responses)
    average_score = total_score / total_assessments
    
    # Status band distribution
    status_distribution = {}
    for response in responses:
        status = response.status_band
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    # Category averages
    category_totals = {}
    for response in responses:
        for category, data in response.category_scores.items():
            if category not in category_totals:
                category_totals[category] = []
            
            # Handle both dict and numeric values
            if isinstance(data, dict):
                score = data.get('score', 0)
            else:
                score = data
            category_totals[category].append(score)
    
    category_averages = {
        cat: sum(scores) / len(scores) if scores else 0
        for cat, scores in category_totals.items()
    }
    
    # Demographic breakdown
    demographics = {
        "by_gender": {},
        "by_nationality": {},
        "by_employment": {},
        "by_income_range": {},
        "by_emirate": {}
    }
    
    for response in responses:
        profile = db.query(FinancialClinicProfile).filter(
            FinancialClinicProfile.id == response.profile_id
        ).first()
        
        if profile:
            # Gender breakdown
            gender = profile.gender
            if gender not in demographics["by_gender"]:
                demographics["by_gender"][gender] = {"count": 0, "avg_score": []}
            demographics["by_gender"][gender]["count"] += 1
            demographics["by_gender"][gender]["avg_score"].append(response.total_score)
            
            # Nationality breakdown
            nationality = profile.nationality
            if nationality not in demographics["by_nationality"]:
                demographics["by_nationality"][nationality] = {"count": 0, "avg_score": []}
            demographics["by_nationality"][nationality]["count"] += 1
            demographics["by_nationality"][nationality]["avg_score"].append(response.total_score)
            
            # Employment breakdown
            employment = profile.employment_status
            if employment not in demographics["by_employment"]:
                demographics["by_employment"][employment] = {"count": 0, "avg_score": []}
            demographics["by_employment"][employment]["count"] += 1
            demographics["by_employment"][employment]["avg_score"].append(response.total_score)
            
            # Income range breakdown
            income = profile.income_range
            if income not in demographics["by_income_range"]:
                demographics["by_income_range"][income] = {"count": 0, "avg_score": []}
            demographics["by_income_range"][income]["count"] += 1
            demographics["by_income_range"][income]["avg_score"].append(response.total_score)
            
            # Emirate breakdown
            emirate = profile.emirate
            if emirate not in demographics["by_emirate"]:
                demographics["by_emirate"][emirate] = {"count": 0, "avg_score": []}
            demographics["by_emirate"][emirate]["count"] += 1
            demographics["by_emirate"][emirate]["avg_score"].append(response.total_score)
    
    # Calculate averages for demographics
    for category in demographics:
        for key in demographics[category]:
            scores = demographics[category][key]["avg_score"]
            demographics[category][key]["avg_score"] = sum(scores) / len(scores) if scores else 0
    
    return {
        "company_name": company.company_name,
        "company_url": company_url,
        "total_assessments": total_assessments,
        "average_score": round(average_score, 2),
        "status_distribution": status_distribution,
        "category_averages": {k: round(v, 2) for k, v in category_averages.items()},
        "demographic_breakdown": demographics,
        "created_at": company.created_at.isoformat() if company.created_at else None
    }


@router.get("/company/{company_url}/submissions")
async def get_company_financial_clinic_submissions(
    company_url: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get paginated list of Financial Clinic submissions for a company.
    Admin only.
    
    Returns individual submission details (anonymized) for analysis.
    """
    from app.models import CompanyTracker, FinancialClinicResponse, FinancialClinicProfile
    
    # Get company
    company = db.query(CompanyTracker).filter(
        CompanyTracker.unique_url == company_url
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get responses with pagination
    responses = db.query(FinancialClinicResponse).filter(
        FinancialClinicResponse.company_tracker_id == company.id
    ).order_by(FinancialClinicResponse.created_at.desc()).offset(skip).limit(limit).all()
    
    # Get total count
    total_count = db.query(FinancialClinicResponse).filter(
        FinancialClinicResponse.company_tracker_id == company.id
    ).count()
    
    submissions = []
    for response in responses:
        profile = db.query(FinancialClinicProfile).filter(
            FinancialClinicProfile.id == response.profile_id
        ).first()
        
        submissions.append({
            "id": response.id,
            "total_score": response.total_score,
            "status_band": response.status_band,
            "category_scores": response.category_scores,
            "questions_answered": response.questions_answered,
            "created_at": response.created_at.isoformat() if response.created_at else None,
            # Anonymized profile data (no email/name)
            "demographics": {
                "gender": profile.gender if profile else None,
                "nationality": profile.nationality if profile else None,
                "employment_status": profile.employment_status if profile else None,
                "income_range": profile.income_range if profile else None,
                "emirate": profile.emirate if profile else None,
                "children": profile.children if profile else 0
            }
        })
    
    return {
        "company_name": company.company_name,
        "company_url": company_url,
        "total_count": total_count,
        "skip": skip,
        "limit": limit,
        "submissions": submissions
    }


@router.get("/export-csv")
async def export_all_financial_clinic_csv(
    company_url: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Export Financial Clinic submissions to CSV format.
    Admin only.
    
    Can filter by company_url and date range.
    Returns CSV file with all submission data including user demographics and mobile numbers.
    """
    import csv
    from fastapi.responses import StreamingResponse
    
    from app.models import CompanyTracker, FinancialClinicResponse, FinancialClinicProfile
    
    # Build query
    query = db.query(FinancialClinicResponse)
    
    # Filter by company if specified
    company = None
    if company_url:
        company = db.query(CompanyTracker).filter(
            CompanyTracker.unique_url == company_url
        ).first()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        query = query.filter(FinancialClinicResponse.company_tracker_id == company.id)
    
    # Filter by date range
    if start_date:
        query = query.filter(FinancialClinicResponse.created_at >= start_date)
    if end_date:
        query = query.filter(FinancialClinicResponse.created_at <= end_date)
    
    # Get all responses
    responses = query.order_by(FinancialClinicResponse.created_at.desc()).all()
    
    # Create CSV content
    output = io.StringIO()
    
    fieldnames = [
        'id', 'name', 'email', 'mobile_number', 'date_of_birth', 'gender', 
        'nationality', 'children', 'employment_status', 'income_range', 'emirate',
        'total_score', 'status_band', 'questions_answered', 'created_at'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for response in responses:
        profile = db.query(FinancialClinicProfile).filter(
            FinancialClinicProfile.id == response.profile_id
        ).first()
        
        if profile:
            row = {
                'id': response.id,
                'name': profile.name,
                'email': profile.email,
                'mobile_number': profile.mobile_number or '',
                'date_of_birth': profile.date_of_birth,
                'gender': profile.gender,
                'nationality': profile.nationality,
                'children': profile.children,
                'employment_status': profile.employment_status,
                'income_range': profile.income_range,
                'emirate': profile.emirate,
                'total_score': response.total_score,
                'status_band': response.status_band,
                'questions_answered': response.questions_answered,
                'created_at': response.created_at.isoformat() if response.created_at else ''
            }
            writer.writerow(row)
    
    # Prepare response
    output.seek(0)
    
    # Generate filename
    if company:
        filename = f"{company.company_name.replace(' ', '_')}_financial_clinic_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        filename = f"financial_clinic_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/company/{company_url}/export-csv")
async def export_company_financial_clinic_csv(
    company_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Export Financial Clinic submissions for a specific company to CSV format.
    Admin only.
    
    Returns CSV file with all submission data including user demographics and mobile numbers.
    """
    # Delegate to the general export endpoint with company filter
    return await export_all_financial_clinic_csv(
        company_url=company_url,
        db=db,
        current_user=current_user
    )
