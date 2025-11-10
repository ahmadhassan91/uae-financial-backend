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
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import io
from datetime import datetime

from ..database import get_db
from ..models import User, CustomerProfile, SurveyResponse, Product
from ..auth.dependencies import get_current_user
from .financial_clinic_questions import get_questions_for_profile, FINANCIAL_CLINIC_QUESTIONS
from .financial_clinic_scoring import calculate_financial_clinic_score, FinancialClinicScorer
from .financial_clinic_insights import generate_insights
from .financial_clinic_products import get_product_recommendations

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financial-clinic", tags=["Financial Clinic"])


# ==================== Request/Response Models ====================

class FinancialClinicAnswers(BaseModel):
    """Survey answers submission."""
    responses: Dict[str, int]  # question_id -> answer_value (1-5)
    has_children: bool = False


class ProfileData(BaseModel):
    """Customer profile data for recommendations."""
    # Required fields
    name: str
    date_of_birth: str  # Format: DD/MM/YYYY
    gender: str  # Male, Female
    nationality: str  # Emirati, Non-Emirati
    children: int  # 0-5+
    employment_status: str  # Employed, Self-Employed, Unemployed
    income_range: str  # Below 5K, 5K-10K, etc.
    emirate: str  # Dubai, Abu Dhabi, Sharjah, etc.
    email: str
    
    # Optional fields
    mobile_number: Optional[str] = None


class FinancialClinicCalculateRequest(BaseModel):
    """Request for score calculation."""
    answers: Dict[str, int]
    profile: ProfileData


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
    language: str = "en"
):
    """
    Get Financial Clinic questions based on profile.
    
    Args:
        children: Number of children (0 = no children, >= 1 = has children)
        language: "en" or "ar"
        
    Returns:
        14 or 15 questions depending on children count:
        - If children = 0: Returns 14 questions (Q15 excluded)
        - If children > 0: Returns all 15 questions (Q15 included)
    """
    # Get questions based on children count
    questions = get_questions_for_profile(children_count=children)
    
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
    
    # Calculate results first
    result = await calculate_financial_clinic_result(request, db)
    
    # Convert Pydantic model to dict
    result_dict = result.dict() if hasattr(result, 'dict') else result
    
    # Save to database
    try:
        # 1. Create or get profile
        profile_data = request.profile.dict() if request.profile else {}
        
        # Check if profile exists by email
        existing_profile = None
        if profile_data.get('email'):
            existing_profile = db.query(FinancialClinicProfile).filter(
                FinancialClinicProfile.email == profile_data['email']
            ).first()
        
        if existing_profile:
            # Update existing profile
            for key, value in profile_data.items():
                if hasattr(existing_profile, key) and value is not None:
                    setattr(existing_profile, key, value)
            profile = existing_profile
        else:
            # Create new profile
            profile = FinancialClinicProfile(
                name=profile_data.get('name', ''),
                date_of_birth=profile_data.get('date_of_birth', ''),
                gender=profile_data.get('gender', ''),
                nationality=profile_data.get('nationality', ''),
                children=profile_data.get('children', 0),
                employment_status=profile_data.get('employment_status', ''),
                income_range=profile_data.get('income_range', ''),
                emirate=profile_data.get('emirate', ''),
                email=profile_data.get('email', ''),
                mobile_number=profile_data.get('mobile_number')
            )
            db.add(profile)
            db.flush()  # Get profile.id
        
        # 2. Create survey response
        survey_response = FinancialClinicResponse(
            profile_id=profile.id,
            answers=request.answers,
            total_score=result_dict['total_score'],
            status_band=result_dict['status_band'],
            category_scores=result_dict['category_scores'],
            insights=result_dict.get('insights', []),
            product_recommendations=result_dict.get('products', []),
            questions_answered=result_dict.get('questions_answered', len(request.answers)),
            total_questions=result_dict.get('total_questions', 15)
        )
        db.add(survey_response)
        db.commit()
        db.refresh(survey_response)
        
        # 3. Return results with survey_response_id
        return {
            **result_dict,
            "survey_response_id": survey_response.id,
            "saved_at": survey_response.created_at.isoformat() if survey_response.created_at else None
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
        pdf_content = service.generate_financial_clinic_pdf(
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
        
        # Generate PDF
        pdf_content = report_service.generate_financial_clinic_pdf(
            survey_data=survey_data,
            language=request.language
        )
        
        # Send email with PDF attachment
        email_result = await email_service.send_financial_clinic_report(
            recipient_email=request.email,
            result=survey_data['result'],
            pdf_content=pdf_content,
            profile=survey_data['profile'],
            language=request.language
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
