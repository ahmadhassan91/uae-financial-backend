from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
import pytz

def parse_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    # Try ISO format first (e.g., 2026-01-20T00:00:00.000Z from frontend)
    try:
        if 'T' in date_str:
            # Remove 'Z' suffix if present and parse
            clean_date = date_str.replace('Z', '+00:00')
            if clean_date.endswith('+00:00'):
                 return datetime.fromisoformat(clean_date.replace('+00:00', ''))
            return datetime.fromisoformat(clean_date)
        else:
            # Try YYYY-MM-DD format
            return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None

def apply_date_range_filter(query, date_range: str, start_date: Optional[str] = None, end_date: Optional[str] = None, model=None):
    """
    Apply date range filtering to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        date_range: Predefined date range ('7d', '30d', '90d', '1y', 'ytd', 'all')
        start_date: Custom start date (YYYY-MM-DD format)
        end_date: Custom end date (YYYY-MM-DD format)
        model: The model containing 'created_at' field (defaults to FinancialClinicResponse)
        
    Returns:
        Filtered query
    """
    if model is None:
        from app.models import FinancialClinicResponse
        model = FinancialClinicResponse

    # If custom date range is provided, use it
    if start_date or end_date:
        start_dt = parse_date(start_date) if start_date else None
        end_dt = parse_date(end_date) if end_date else None
        
        if start_dt:
            query = query.filter(model.created_at >= start_dt)
        if end_dt:
            # Add 1 day to include the end date fully
            end_dt = end_dt + timedelta(days=1)
            query = query.filter(model.created_at < end_dt)
        
        # Return early if we applied custom date filters
        if start_dt or end_dt:
            return query
    
    # Apply predefined date range filters
    now = datetime.now(pytz.UTC)
    
    if date_range == "7d":
        start_date_dt = now - timedelta(days=7)
        query = query.filter(model.created_at >= start_date_dt)
    elif date_range == "30d":
        start_date_dt = now - timedelta(days=30)
        query = query.filter(model.created_at >= start_date_dt)
    elif date_range == "90d":
        start_date_dt = now - timedelta(days=90)
        query = query.filter(model.created_at >= start_date_dt)
    elif date_range == "1y":
        start_date_dt = now - timedelta(days=365)
        query = query.filter(model.created_at >= start_date_dt)
    elif date_range == "ytd":
        # Year to date - from January 1st of current year
        start_date_dt = datetime(now.year, 1, 1).replace(tzinfo=pytz.UTC)
        query = query.filter(model.created_at >= start_date_dt)
    elif date_range == "all":
        # No date filtering for "all time"
        pass
    
    return query

def apply_demographic_filters(query, filters: Dict[str, Any], db: Session):
    """
    Apply demographic filters to a SQLAlchemy query.
    """
    from app.models import FinancialClinicProfile, CompanyTracker, FinancialClinicResponse, CompanyDetails
    
    # Gender filter
    if filters.get('genders'):
        genders = filters['genders']
        if isinstance(genders, str):
            genders = [g.strip() for g in genders.split(',')]
        query = query.filter(FinancialClinicProfile.gender.in_(genders))
    
    # Nationality filter
    if filters.get('nationalities'):
        nationalities = filters['nationalities']
        if isinstance(nationalities, str):
            nationalities = [n.strip() for n in nationalities.split(',')]
        query = query.filter(FinancialClinicProfile.nationality.in_(nationalities))
    
    # Emirate filter
    if filters.get('emirates'):
        emirates = filters['emirates']
        if isinstance(emirates, str):
            emirates = [e.strip() for e in emirates.split(',')]
        query = query.filter(FinancialClinicProfile.emirate.in_(emirates))
    
    # Employment status filter
    if filters.get('employment_statuses'):
        emp_statuses = filters['employment_statuses']
        if isinstance(emp_statuses, str):
            emp_statuses = [es.strip() for es in emp_statuses.split(',')]
        query = query.filter(FinancialClinicProfile.employment_status.in_(emp_statuses))
    
    # Income range filter
    if filters.get('income_ranges'):
        inc_ranges = filters['income_ranges']
        if isinstance(inc_ranges, str):
            inc_ranges = [ir.strip() for ir in inc_ranges.split(',')]
        query = query.filter(FinancialClinicProfile.income_range.in_(inc_ranges))
    
    # Children filter
    if filters.get('children'):
        children_options = filters['children']
        if isinstance(children_options, str):
            children_options = [c.strip() for c in children_options.split(',')]
            
        children_conditions = []
        for child_option in children_options:
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
    
    # Unique URL filter (CompanyTracker)
    if filters.get('companies'):
        companies = filters['companies']
        if isinstance(companies, str):
            companies = [c.strip() for c in companies.split(',')]
            
        company_trackers = db.query(CompanyTracker).filter(
            or_(
                CompanyTracker.company_name.in_(companies),
                CompanyTracker.unique_url.in_(companies)
            )
        ).all()
        company_ids = [c.id for c in company_trackers]
        
        if company_ids:
            query = query.filter(FinancialClinicResponse.company_tracker_id.in_(company_ids))
        else:
            # If no companies found, we want an empty result
            query = query.filter(FinancialClinicResponse.id == -1)

    # Exclude Unique URLs filter
    if filters.get('exclude_unique_urls'):
        query = query.filter(FinancialClinicResponse.company_tracker_id.is_(None))

    # Company filter (CompanyDetails and Free-text)
    if filters.get('activeCompanies'):
        active_comps = filters['activeCompanies']
        if isinstance(active_comps, str):
            active_comps = [ac.strip() for ac in active_comps.split(',')]
            
        active_company_ids = []
        free_text_names = []
        
        for ac in active_comps:
            if str(ac).isdigit():
                active_company_ids.append(int(ac))
            elif str(ac).startswith('free_text:'):
                free_text_names.append(ac.replace('free_text:', '', 1))
            elif ac == 'blank':
                # Handled by separate logic if needed, but adding here for safety
                pass
        
        from sqlalchemy import or_
        conditions = []
        if active_company_ids:
            conditions.append(FinancialClinicProfile.company_details_id.in_(active_company_ids))
        if free_text_names:
            conditions.append(FinancialClinicProfile.company_name.in_(free_text_names))
            
        if conditions:
            query = query.filter(or_(*conditions))

    # Search filter (name, email, phone, company name)
    if filters.get('search'):
        from sqlalchemy import or_
        search = filters['search']
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                FinancialClinicProfile.name.ilike(search_term),
                FinancialClinicProfile.email.ilike(search_term),
                FinancialClinicProfile.mobile_number.ilike(search_term),
                FinancialClinicProfile.company_name.ilike(search_term)
            )
        )

    # Company name filter (from Submissions tab dropdown)
    if filters.get('company_name'):
        company_name = filters['company_name']
        query = query.filter(FinancialClinicProfile.company_name.ilike(f"%{company_name}%"))

    # Status band filter
    if filters.get('status_band') and filters['status_band'] != 'all':
        query = query.filter(FinancialClinicResponse.status_band == filters['status_band'])

    return query

def parse_filter_params(
    age_groups: Optional[str] = None,
    genders: Optional[str] = None,
    nationalities: Optional[str] = None,
    emirates: Optional[str] = None,
    employment_statuses: Optional[str] = None,
    income_ranges: Optional[str] = None,
    children: Optional[str] = None,
    companies: Optional[str] = None,
    activeCompanies: Optional[str] = None
) -> Dict[str, Any]:
    """Parse comma-separated filter parameters into lists."""
    filters = {}
    if age_groups: filters['age_groups'] = [ag.strip() for ag in age_groups.split(',')]
    if genders: filters['genders'] = [g.strip() for g in genders.split(',')]
    if nationalities: filters['nationalities'] = [n.strip() for n in nationalities.split(',')]
    if emirates: filters['emirates'] = [e.strip() for e in emirates.split(',')]
    if employment_statuses: filters['employment_statuses'] = [es.strip() for es in employment_statuses.split(',')]
    if income_ranges: filters['income_ranges'] = [ir.strip() for ir in income_ranges.split(',')]
    if children: filters['children'] = [c.strip() for c in children.split(',')]
    if companies: filters['companies'] = [c.strip() for c in companies.split(',')]
    if activeCompanies: filters['activeCompanies'] = [ac.strip() for ac in activeCompanies.split(',')]
    return filters
