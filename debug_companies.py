from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CompanyDetails, CompanyTracker

router = APIRouter()

@router.get("/debug-companies")
async def debug_companies(db: Session = Depends(get_db)):
    """Debug endpoint to check company data sources"""
    
    # Get CompanyDetails (new system)
    details = db.query(CompanyDetails).filter(CompanyDetails.is_active == True).order_by(CompanyDetails.company_name).all()
    details_list = [{"id": c.id, "name": c.company_name} for c in details]
    
    # Get CompanyTracker (old system)
    trackers = db.query(CompanyTracker).filter(CompanyTracker.is_active == True).order_by(CompanyTracker.company_name).all()
    trackers_list = [{"id": c.id, "name": c.company_name, "url": c.unique_url} for c in trackers]
    
    # Check which chart companies are in which system
    chart_companies = ['Al Ghadeer UAE', 'Al Ghadeer KSA', 'Al Maha']
    
    details_matches = []
    tracker_matches = []
    
    for company in chart_companies:
        if any(c.company_name == company for c in details):
            details_matches.append(company)
        if any(c.company_name == company for c in trackers):
            tracker_matches.append(company)
    
    return {
        "company_details": {
            "count": len(details),
            "companies": details_list[:10],  # First 10
            "chart_matches": details_matches
        },
        "company_tracker": {
            "count": len(trackers),
            "companies": trackers_list[:10],  # First 10
            "chart_matches": tracker_matches
        },
        "conclusion": {
            "charts_should_use": "company_details" if details_matches else "company_tracker",
            "charts_currently_show": "company_details" if details_matches else "unknown"
        }
    }
