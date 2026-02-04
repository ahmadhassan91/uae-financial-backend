from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from datetime import datetime
import csv
import io
import logging
import os

from app.models import FinancialClinicResponse, FinancialClinicProfile, IncompleteSurvey, CompanyTracker, ConsultationRequest
from app.admin.utils import apply_date_range_filter, apply_demographic_filters, parse_date

logger = logging.getLogger(__name__)

class ConsolidatedExportService:
    def __init__(self, db: Session):
        self.db = db

    def generate_csv(self, filters: Dict[str, Any] = None) -> io.StringIO:
        """
        Generates a consolidated CSV containing Submissions, Leads, and Incomplete surveys.
        Uses the SAME format as existing export-csv endpoint.
        """
        if filters is None:
            filters = {}

        # 1. Fetch Completed/Lead Data (FinancialClinicResponse)
        responses_query = self.db.query(FinancialClinicResponse, FinancialClinicProfile).join(
            FinancialClinicProfile,
            FinancialClinicResponse.profile_id == FinancialClinicProfile.id
        )

        # 2. Fetch Incomplete Data (IncompleteSurvey)
        incomplete_query = self.db.query(IncompleteSurvey)

        # Apply Date Range Filters
        date_range = filters.get('date_range', 'all')
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')

        responses_query = apply_date_range_filter(responses_query, date_range, start_date, end_date, model=FinancialClinicResponse)
        incomplete_query = apply_date_range_filter(incomplete_query, date_range, start_date, end_date, model=IncompleteSurvey)

        # Apply Legacy Company Filters
        company_id = filters.get('company_id')
        if company_id:
            responses_query = responses_query.filter(FinancialClinicResponse.company_tracker_id == company_id)
            incomplete_query = incomplete_query.filter(IncompleteSurvey.company_id == company_id)

        # Apply Exclude Unique URLs Filter
        if filters.get('exclude_unique_urls'):
            responses_query = responses_query.filter(FinancialClinicResponse.company_tracker_id.is_(None))
            incomplete_query = incomplete_query.filter(IncompleteSurvey.company_id.is_(None))

        # Apply Demographic and Active Company Filters to Responses
        responses_query = apply_demographic_filters(responses_query, filters, self.db)

        # Execute Queries
        responses = responses_query.order_by(FinancialClinicResponse.created_at.desc()).all()
        incomplete_surveys = incomplete_query.order_by(IncompleteSurvey.created_at.desc()).all()

        # Prepare CSV using SAME format as export-csv
        output = io.StringIO()
        writer = csv.writer(output)

        # Check if Companies Module is enabled
        companies_module_enabled = os.environ.get("COMPANIES_MODULE_ENABLED", "true").lower() == "true"

        # Header - SAME as export-csv but with Status and Consultation columns
        base_headers = [
            'ID', 'Name', 'Email', 'Mobile Number', 'Age', 'Gender', 'Nationality', 'Emirate', 'Children',
            'Employment Status', 'Income Range'
        ]
        if companies_module_enabled:
            base_headers.append('Company')
            base_headers.append('Unique URL')
        base_headers.extend([
            'Total Score', 'Status Band',
            'Questions Answered', 'Income Stream Score', 'Savings Habit Score',
            'Debt Management Score', 'Retirement Planning Score', 'Financial Protection Score',
            'Financial Knowledge Score', 'Leads Requested', 'Action Plan 1', 'Action Plan 2', 'Action Plan 3', 
            'Action Plan 4', 'Action Plan 5', 'Submission Date',
            'Consultation Status', 'Consultation Source', 'Preferred Contact Method',
            'Preferred Time', 'Message', 'Consultation Created At', 'Contacted At', 'Scheduled At', 'Notes',
            'Current Step', 'Total Steps', 'Completion %', 'Status'
        ])
        writer.writerow(base_headers)

        # Fetch all consultation requests for the responses
        response_ids = [r[0].id for r in responses]
        consultation_map = {}
        if response_ids:
            consultations = self.db.query(ConsultationRequest).filter(
                ConsultationRequest.survey_response_id.in_(response_ids)
            ).all()
            for c in consultations:
                consultation_map[c.survey_response_id] = c

        # Process Responses (Submissions & Leads)
        for response, profile in responses:
            status = "Lead" if response.leads_requested else "Submitted"

            # Use profile_snapshot if available
            if response.profile_snapshot:
                profile_data = response.profile_snapshot
            else:
                profile_data = {
                    'name': profile.name,
                    'email': profile.email,
                    'mobile_number': profile.mobile_number,
                    'date_of_birth': profile.date_of_birth,
                    'gender': profile.gender,
                    'nationality': profile.nationality,
                    'emirate': profile.emirate,
                    'children': profile.children,
                    'employment_status': profile.employment_status,
                    'income_range': profile.income_range,
                    'company_name': profile.company_name if hasattr(profile, 'company_name') else '',
                }

            age = self._calculate_age(profile_data.get('date_of_birth', ''))
            
            # Extract category scores
            income_stream_score = self._get_category_score(response.category_scores, 'Income Stream')
            savings_habit_score = self._get_category_score(response.category_scores, 'Savings Habit')
            debt_management_score = self._get_category_score(response.category_scores, 'Debt Management')
            retirement_planning_score = self._get_category_score(response.category_scores, 'Retirement Planning')
            financial_protection_score = self._get_category_score(response.category_scores, 'Protecting Your Family')
            financial_knowledge_score = self._get_category_score(response.category_scores, 'Emergency Savings')

            # Extract insights
            insights = self._extract_insights(response.insights)

            # Format mobile number
            mobile_number = profile_data.get('mobile_number', '')
            if mobile_number and not mobile_number.startswith('+'):
                mobile_number = '+971 ' + mobile_number

            # Get consultation data
            consultation = consultation_map.get(response.id)
            
            # Helper to get unique URL
            unique_url = ''
            if response.company_tracker:
                unique_url = response.company_tracker.unique_url
            elif response.company_tracker_id:
                 # Fallback if relationship not loaded but ID exists
                 tracker = self.db.query(CompanyTracker).filter(CompanyTracker.id == response.company_tracker_id).first()
                 if tracker:
                     unique_url = tracker.unique_url

            # Build row
            row_data = [
                response.id,
                profile_data.get('name', ''),
                profile_data.get('email', ''),
                mobile_number,
                age,
                profile_data.get('gender', ''),
                profile_data.get('nationality', ''),
                profile_data.get('emirate', ''),
                profile_data.get('children', ''),
                profile_data.get('employment_status', ''),
                profile_data.get('income_range', ''),
            ]
            if companies_module_enabled:
                row_data.append(profile_data.get('company_name', ''))
                row_data.append(unique_url)
            row_data.extend([
                round(response.total_score, 2) if response.total_score else 0,
                response.status_band if response.status_band else '',
                response.questions_answered if response.questions_answered else 0,
                income_stream_score,
                savings_habit_score,
                debt_management_score,
                retirement_planning_score,
                financial_protection_score,
                financial_knowledge_score,
                'Y' if response.leads_requested else 'N',
                insights[0], insights[1], insights[2], insights[3], insights[4],
                response.created_at.strftime('%Y-%m-%d %H:%M:%S') if response.created_at else '',
                consultation.status if consultation else '',
                consultation.source if consultation else '',
                consultation.preferred_contact_method if consultation else '',
                consultation.preferred_time if consultation else '',
                consultation.message if consultation else '',
                consultation.created_at.strftime('%Y-%m-%d %H:%M:%S') if consultation and consultation.created_at else '',
                consultation.contacted_at.strftime('%Y-%m-%d %H:%M:%S') if consultation and consultation.contacted_at else '',
                consultation.scheduled_at.strftime('%Y-%m-%d %H:%M:%S') if consultation and consultation.scheduled_at else '',
                consultation.notes if consultation else '',
                0,  # Current Step
                response.total_questions if response.total_questions else 15,
                100,  # Completion %
                status
            ])
            writer.writerow(row_data)

        # Process Incomplete Surveys
        for survey in incomplete_surveys:
            # Check demographic filters for incomplete surveys (Python-side)
            if not self._matches_filters(survey, filters):
                continue

            survey_responses = survey.responses or {}
            
            email = survey.email or survey_responses.get('email', '')
            phone = survey.phone_number or survey_responses.get('mobile_number', '')
            if phone and not phone.startswith('+'):
                phone = '+971 ' + phone

            comp_name = ''
            if survey.company:
                comp_name = survey.company.company_name

            completion_pct = 0
            if survey.total_steps > 0:
                completion_pct = round((survey.current_step / survey.total_steps) * 100, 1)

            row_data = [
                f"INC-{survey.id}",
                survey_responses.get('name', ''),
                email,
                phone,
                survey_responses.get('age', ''),
                survey_responses.get('gender', ''),
                survey_responses.get('nationality', ''),
                survey_responses.get('emirate', ''),
                survey_responses.get('children', ''),
                survey_responses.get('employment_status', ''),
                survey_responses.get('income_range', ''),
            ]
            if companies_module_enabled:
                row_data.append(comp_name)
                # Determine Unique URL: prefer explicit URL, fall back to company tracker's URL
                inc_unique_url = survey.company_url
                if not inc_unique_url and survey.company:
                    inc_unique_url = survey.company.unique_url
                row_data.append(inc_unique_url or '')
            row_data.extend([
                '',  # Total Score
                '',  # Status Band
                survey.current_step,  # Questions Answered
                '', '', '', '', '', '',  # Category scores
                'N',  # Leads Requested
                '', '', '', '', '',  # Insights
                survey.created_at.strftime('%Y-%m-%d %H:%M:%S') if survey.created_at else '',
                '', '', '', '', '', '', '', '', '',  # Consultation fields
                survey.current_step,  # Current Step
                survey.total_steps,  # Total Steps
                completion_pct,  # Completion %
                'Incomplete'
            ])
            writer.writerow(row_data)

        return output

    def _calculate_age(self, dob_str):
        if not dob_str or (isinstance(dob_str, str) and dob_str.strip() == ''):
            return ''
        try:
            dob = datetime.strptime(dob_str.strip(), '%d/%m/%Y')
            today = datetime.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            try:
                dob = datetime.strptime(dob_str.strip(), '%Y-%m-%d')
                today = datetime.today()
                return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except:
                return ''

    def _get_category_score(self, category_scores, category_name):
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

    def _extract_insights(self, insights):
        result = ['', '', '', '', '']
        if not insights:
            return result
        try:
            if isinstance(insights, list):
                insight_texts = []
                for insight in insights[:5]:
                    if isinstance(insight, dict):
                        text = insight.get('text', '') or insight.get('title', '') or insight.get('message', '') or insight.get('description', '')
                        if text:
                            insight_texts.append(text)
                    elif isinstance(insight, str):
                        insight_texts.append(insight)
                return insight_texts + [''] * (5 - len(insight_texts))
            elif isinstance(insights, str):
                return [insights] + [''] * 4
            else:
                return [str(insights)] + [''] * 4
        except:
            return result

    def _matches_filters(self, survey: IncompleteSurvey, filters: Dict[str, Any]) -> bool:
        """Helper to match incomplete surveys against demographics in Python."""
        responses = survey.responses or {}
        
        # Gender
        if filters.get('genders'):
            genders = filters['genders']
            if isinstance(genders, str):
                genders = [g.strip() for g in genders.split(',')]
            survey_gender = responses.get('gender')
            if survey_gender and survey_gender not in genders:
                return False
        
        # Nationality
        if filters.get('nationalities'):
            nationalities = filters['nationalities']
            if isinstance(nationalities, str):
                nationalities = [n.strip() for n in nationalities.split(',')]
            survey_nationality = responses.get('nationality')
            if survey_nationality and survey_nationality not in nationalities:
                return False
        
        # Emirate
        if filters.get('emirates'):
            emirates = filters['emirates']
            if isinstance(emirates, str):
                emirates = [e.strip() for e in emirates.split(',')]
            survey_emirate = responses.get('emirate')
            if survey_emirate and survey_emirate not in emirates:
                return False
        
        return True
