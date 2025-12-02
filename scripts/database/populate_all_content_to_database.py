#!/usr/bin/env python3
"""
Populate all frontend content into the database for localization management.

This script extracts all UI elements, questions, and other content from the frontend
and populates them into the LocalizedContent table so admins can manage translations
through the admin interface.
"""
import asyncio
import sys
import os
from typing import Dict, List, Any

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.localization.service import LocalizationService
from app.models import LocalizedContent


# All UI elements from LocalizationContext
UI_ELEMENTS = {
    # Navigation and UI
    'welcome_message': 'Welcome to Financial Health Assessment',
    'start_survey': 'Start Assessment',
    'next_question': 'Next Question',
    'previous_question': 'Previous Question',
    'submit_survey': 'Submit Assessment',
    'your_results': 'Your Results',
    'download_pdf': 'Download Report',
    'send_email': 'Send via Email',
    'register_account': 'Create Account',
    'language_selector': 'Select Language',
    'continue_assessment': 'Continue Assessment',
    'begin_assessment_now': 'Begin Assessment Now',
    'access_previous_results': 'Access Previous Results',
    'view_previous_results': 'View Previous Results',
    
    # Assessment and Scoring
    'financial_health_score': 'Financial Health Score',
    'recommendations': 'Recommendations',
    'budgeting': 'Budgeting',
    'savings': 'Savings',
    'debt_management': 'Debt Management',
    'financial_planning': 'Financial Planning',
    'investment_knowledge': 'Investment Knowledge',
    'income_stream': 'Income Stream',
    'monthly_expenses': 'Monthly Expenses Management',
    'savings_habit': 'Savings Habit',
    'retirement_planning': 'Retirement Planning',
    'protection': 'Protecting Your Assets & Loved Ones',
    'future_planning': 'Planning for Your Future & Siblings',
    
    # Score Interpretations
    'excellent': 'Excellent',
    'good': 'Good',
    'fair': 'Fair',
    'needs_improvement': 'Needs Improvement',
    'poor': 'Poor',
    'at_risk': 'At Risk',
    
    # Personal Information
    'personal_information': 'Personal Information',
    'first_name': 'First Name',
    'last_name': 'Last Name',
    'age': 'Age',
    'gender': 'Gender',
    'male': 'Male',
    'female': 'Female',
    'other': 'Other',
    'prefer_not_to_say': 'Prefer not to say',
    'nationality': 'Nationality',
    'emirate': 'Emirate',
    'employment_status': 'Employment Status',
    'employment_sector': 'Employment Sector',
    'monthly_income': 'Monthly Income',
    'income_range': 'Income Range',
    'household_size': 'Household Size',
    'children': 'Children',
    'residence': 'Residence',
    'yes': 'Yes',
    'no': 'No',
    'email': 'Email Address',
    'phone_number': 'Phone Number',
    
    # Actions
    'save': 'Save',
    'cancel': 'Cancel',
    'edit': 'Edit',
    'delete': 'Delete',
    'confirm': 'Confirm',
    'back': 'Back',
    'continue': 'Continue',
    'complete': 'Complete',
    'skip': 'Skip',
    
    # Status Messages
    'loading': 'Loading...',
    'error': 'Error',
    'success': 'Success',
    'warning': 'Warning',
    'info': 'Information',
    
    # Authentication
    'sign_in': 'Sign In',
    'sign_out': 'Sign Out',
    'sign_up': 'Sign Up',
    'welcome_back': 'Welcome back!',
    'date_of_birth': 'Date of Birth',
    
    # Landing Page
    'financial_health_assessment': 'Financial Health Assessment',
    'trusted_uae_institution': 'A trusted UAE financial institution providing transparent, science-based financial wellness assessment.',
    'get_personalized_insights': 'Get personalized insights to strengthen your financial future.',
    'transparent_scoring': 'Transparent Scoring',
    'privacy_protected': 'Privacy Protected',
    'personalized_insights': 'Personalized Insights',
    'progress_tracking': 'Progress Tracking',
    'science_based_methodology': 'Science-Based Methodology',
    'uae_specific_insights': 'UAE-Specific Insights',
    'ready_to_improve': 'Ready to Improve Your Financial Health?',
    'join_thousands': 'Join thousands of UAE residents who have strengthened their financial future with our comprehensive assessment.',
    
    # Assessment Flow
    'progress_overview': 'Progress Overview',
    'questions_total': 'questions total',
    'current': 'Current',
    'completed': 'Completed',
    'pending': 'Pending',
    'complete_assessment': 'Complete Assessment',
    'strongly_agree': 'Strongly Agree',
    'agree': 'Agree',
    'neutral': 'Neutral',
    'disagree': 'Disagree',
    'strongly_disagree': 'Strongly Disagree',
    
    # Results and Reports
    'overall_score': 'Overall Score',
    'pillar_breakdown': 'Pillar Breakdown',
    'detailed_recommendations': 'Detailed Recommendations',
    'action_plan': 'Action Plan',
    'next_steps': 'Next Steps',
    'download_report': 'Download Report',
    'email_report': 'Email Report',
    'share_results': 'Share Results',
    
    # Error Messages
    'error_loading_questions': 'Error loading questions. Please try again.',
    'error_saving_response': 'Error saving response. Please try again.',
    'error_generating_report': 'Error generating report. Please try again.',
    'network_error': 'Network error. Please check your connection.',
    
    # Validation Messages
    'field_required': 'This field is required',
    'invalid_email': 'Please enter a valid email address',
    'invalid_date': 'Please enter a valid date',
    'please_select_option': 'Please select an option',
    
    # Additional UI
    'of': 'of',
    
    # Landing Page Extended Content
    'transparent_scoring_description': 'Understand exactly how your score is calculated with clear explanations for each factor.',
    'privacy_protected_description': 'Your data is handled according to UAE PDPL regulations with full consent management.',
    'personalized_insights_description': 'Receive tailored recommendations based on your unique financial situation and goals.',
    'progress_tracking_description': 'Save your results with just email and date of birth. No passwords needed to track your progress over time.',
    'about_financial_health_assessment': 'About Financial Health Assessment',
    'science_based_methodology_description': 'Our assessment uses proven financial wellness metrics adapted specifically for UAE residents. The scoring system evaluates five key pillars of financial health.',
    'budgeting_expense_management': 'Budgeting & Expense Management',
    'savings_emergency_funds': 'Savings & Emergency Funds',
    'financial_planning_goals': 'Financial Planning & Goals',
    'investment_wealth_building': 'Investment & Wealth Building',
    'uae_specific_insights_description': 'Tailored for the UAE market with localized recommendations that consider Emirates-specific financial products, regulations, and cultural factors.',
    'uae_banking_products_services': 'UAE banking products & services',
    'adcb_emirates_nbd_partnerships': 'ADCB & Emirates NBD partnerships',
    'sharia_compliant_options': 'Sharia-compliant options',
    'expat_specific_considerations': 'Expat-specific considerations',
    'local_investment_opportunities': 'Local investment opportunities',
    'save_results_no_passwords': 'Save your results with just your email and date of birth - no passwords required!',
    'continue_your_journey': 'Continue Your Journey',
    
    # Admin Interface
    'admin_dashboard': 'Admin Dashboard',
    'localization_management': 'Localization Management',
    'manage_translations': 'Manage translations and localized content for multiple languages',
    'content_type': 'Content Type',
    'language': 'Language',
    'version': 'Version',
    'status': 'Status',
    'actions': 'Actions',
    'active': 'Active',
    'inactive': 'Inactive',
    'add_content': 'Add Content',
    'new_workflow': 'New Workflow',
    'create_translation_workflow': 'Create Translation Workflow',
    'source_language': 'Source Language',
    'target_language': 'Target Language',
    'workflow_type': 'Workflow Type',
    'priority': 'Priority',
    'content_ids': 'Content IDs',
    'notes': 'Notes',
    'create_workflow': 'Create Workflow',
    'add_localized_content': 'Add Localized Content',
    'create_new_localized_content': 'Create new localized content for questions, recommendations, or UI elements',
    'content_id': 'Content ID',
    'title_optional': 'Title (Optional)',
    'text': 'Text',
    'localized_text_content': 'Localized text content',
    'create_content': 'Create Content',
    'filters': 'Filters',
    'all_types': 'All types',
    'all_languages': 'All languages',
    'active_only': 'Active only',
    'localized_content': 'Localized Content',
    'content_items_found': 'content items found',
    'no_localized_content_found': 'No localized content found',
    'translation_workflows': 'Translation Workflows',
    'active_completed_workflows': 'Active and completed translation workflows',
    'no_translation_workflows_found': 'No translation workflows found',
    'analytics': 'Analytics',
    'workflows': 'Workflows',
    'content': 'Content',
    
    # Customer Profile Form
    'customer_profile': 'Customer Profile',
    'please_provide_information': 'Please provide your information to get personalized recommendations',
    'uae_national': 'UAE National',
    'expat': 'Expat',
    'abu_dhabi': 'Abu Dhabi',
    'dubai': 'Dubai',
    'sharjah': 'Sharjah',
    'ajman': 'Ajman',
    'ras_al_khaimah': 'Ras Al Khaimah',
    'fujairah': 'Fujairah',
    'umm_al_quwain': 'Umm Al Quwain',
    'employed_full_time': 'Employed (Full-time)',
    'employed_part_time': 'Employed (Part-time)',
    'self_employed': 'Self-employed',
    'unemployed': 'Unemployed',
    'retired': 'Retired',
    'student': 'Student',
    'less_than_5000': 'Less than AED 5,000',
    '5000_to_10000': 'AED 5,000 - 10,000',
    '10000_to_20000': 'AED 10,000 - 20,000',
    '20000_to_50000': 'AED 20,000 - 50,000',
    'more_than_50000': 'More than AED 50,000',
    
    # Score Results
    'your_financial_health_score': 'Your Financial Health Score',
    'score_out_of_100': 'Score: {{score}} out of 100',
    'score_interpretation': 'Score Interpretation',
    'pillar_scores': 'Pillar Scores',
    'personalized_recommendations': 'Personalized Recommendations',
    'download_detailed_report': 'Download Detailed Report',
    'email_results': 'Email Results',
    'retake_assessment': 'Retake Assessment',
    
    # Report Delivery
    'report_delivery': 'Report Delivery',
    'send_report_email': 'Send Report via Email',
    'enter_email_address': 'Enter your email address to receive the detailed report',
    'send_report': 'Send Report',
    'download_pdf_report': 'Download PDF Report',
    'generating_report': 'Generating your personalized report...',
    'report_sent_successfully': 'Report sent successfully to your email!',
    'report_generation_failed': 'Failed to generate report. Please try again.',
    'email_sending_failed': 'Failed to send email. Please try again.',
}

# All survey questions from survey-data.ts
SURVEY_QUESTIONS = [
    {
        'id': 'q1_income_stability',
        'text': 'My income is stable and predictable each month.',
        'options': [
            {'value': 5, 'label': 'Strongly Agree'},
            {'value': 4, 'label': 'Agree'},
            {'value': 3, 'label': 'Neutral'},
            {'value': 2, 'label': 'Disagree'},
            {'value': 1, 'label': 'Strongly Disagree'}
        ]
    },
    {
        'id': 'q2_income_sources',
        'text': 'I have more than one source of income (e.g., side business, investments).',
        'options': [
            {'value': 5, 'label': 'Multiple consistent income streams'},
            {'value': 4, 'label': 'Multiple inconsistent income streams'},
            {'value': 3, 'label': 'I have a consistent side income'},
            {'value': 2, 'label': 'A non consistent side income'},
            {'value': 1, 'label': 'My Salary'}
        ]
    },
    {
        'id': 'q3_living_expenses',
        'text': 'I can cover my essential living expenses without financial strain.',
        'options': [
            {'value': 5, 'label': 'Strongly Agree'},
            {'value': 4, 'label': 'Agree'},
            {'value': 3, 'label': 'Neutral'},
            {'value': 2, 'label': 'Disagree'},
            {'value': 1, 'label': 'Strongly Disagree'}
        ]
    },
    {
        'id': 'q4_budget_tracking',
        'text': 'I follow a monthly budget and track my expenses.',
        'options': [
            {'value': 5, 'label': 'Consistently every month'},
            {'value': 4, 'label': 'Frequently but not consistently'},
            {'value': 3, 'label': 'Occasionally'},
            {'value': 2, 'label': 'Adhoc'},
            {'value': 1, 'label': 'No Tracking'}
        ]
    },
    {
        'id': 'q5_spending_control',
        'text': 'I spend less than I earn every month.',
        'options': [
            {'value': 5, 'label': 'Consistently every month'},
            {'value': 4, 'label': 'Frequently but not consistently'},
            {'value': 3, 'label': 'Occasionally'},
            {'value': 2, 'label': 'Adhoc'},
            {'value': 1, 'label': 'Greater or all of my earnings'}
        ]
    },
    {
        'id': 'q6_expense_review',
        'text': 'I regularly review and reduce unnecessary expenses.',
        'options': [
            {'value': 5, 'label': 'Consistently every month'},
            {'value': 4, 'label': 'Frequently but not consistently'},
            {'value': 3, 'label': 'Occasionally'},
            {'value': 2, 'label': 'Adhoc'},
            {'value': 1, 'label': 'No Tracking'}
        ]
    },
    {
        'id': 'q7_savings_rate',
        'text': 'I save from my income every month.',
        'options': [
            {'value': 5, 'label': '20% or more'},
            {'value': 4, 'label': 'Less than 20%'},
            {'value': 3, 'label': 'Less than 10%'},
            {'value': 2, 'label': '5% or less'},
            {'value': 1, 'label': '0%'}
        ]
    },
    {
        'id': 'q8_emergency_fund',
        'text': 'I have an emergency fund to cater for my expenses.',
        'options': [
            {'value': 5, 'label': '6+ months'},
            {'value': 4, 'label': '3 - 6 months'},
            {'value': 3, 'label': '2 months'},
            {'value': 2, 'label': '1 month'},
            {'value': 1, 'label': 'Nil'}
        ]
    },
    {
        'id': 'q9_savings_optimization',
        'text': 'I keep my savings in safe, return generating accounts or investments.',
        'options': [
            {'value': 5, 'label': 'Safe | Seek for return optimization consistently'},
            {'value': 4, 'label': 'Safe | Seek for return optimization most of the times'},
            {'value': 3, 'label': 'Savings Account with minimal returns'},
            {'value': 2, 'label': 'Current Account'},
            {'value': 1, 'label': 'Cash'}
        ]
    },
    {
        'id': 'q10_payment_history',
        'text': 'I pay all my bills and loan installments on time.',
        'options': [
            {'value': 5, 'label': 'Consistently every month'},
            {'value': 4, 'label': 'Frequently but not consistently'},
            {'value': 3, 'label': 'Occasionally'},
            {'value': 2, 'label': 'Adhoc'},
            {'value': 1, 'label': 'Missed Payments most of the times'}
        ]
    },
    {
        'id': 'q11_debt_ratio',
        'text': 'My debt repayments are less than 30% of my monthly income.',
        'options': [
            {'value': 5, 'label': 'No Debt'},
            {'value': 4, 'label': '20% or less of monthly income'},
            {'value': 3, 'label': 'Less than 30% of monthly income'},
            {'value': 2, 'label': '30% or more of monthly income'},
            {'value': 1, 'label': '50% or more of monthly income'}
        ]
    },
    {
        'id': 'q12_credit_score',
        'text': 'I understand my credit score and actively maintain or improve it.',
        'options': [
            {'value': 5, 'label': '100% and monitor it consistently'},
            {'value': 4, 'label': '100% and monitor it frequently'},
            {'value': 3, 'label': 'somewhat understand and frequent monitoring'},
            {'value': 2, 'label': 'somewhat understand and maintain on an adhoc basis'},
            {'value': 1, 'label': 'No Understanding and not maintained'}
        ]
    },
    {
        'id': 'q13_retirement_planning',
        'text': 'I have a retirement savings plan or pension fund in place to secure a stable income at retirement.',
        'options': [
            {'value': 5, 'label': 'Yes - I have already secured a stable income'},
            {'value': 4, 'label': 'Yes - I am highly confident of having a stable income'},
            {'value': 3, 'label': 'Yes - I am somewhat confident of having a stable income'},
            {'value': 2, 'label': 'No: Planning to have one shortly | adhoc Savings'},
            {'value': 1, 'label': 'No: not for the time being'}
        ]
    },
    {
        'id': 'q14_insurance_coverage',
        'text': 'I have adequate takaful cover (insurance) - (health, life, motor, property).',
        'options': [
            {'value': 5, 'label': '100% adequate cover in place for the required protection'},
            {'value': 4, 'label': '80% cover in place for the required protection'},
            {'value': 3, 'label': '50% cover in place for the required protection'},
            {'value': 2, 'label': '25% cover in place for the required protection'},
            {'value': 1, 'label': 'No Coverage'}
        ]
    },
    {
        'id': 'q15_financial_planning',
        'text': 'I have a written financial plan with goals for the next 3–5 years catering.',
        'options': [
            {'value': 5, 'label': 'Concise Financial plan in place and consistently reviewed'},
            {'value': 4, 'label': 'Broad Financial plan in place and frequently reviewed'},
            {'value': 3, 'label': 'High level objectives set and occasionally reviewed'},
            {'value': 2, 'label': 'Adhoc Plan | reviews'},
            {'value': 1, 'label': 'No Financial Plan in place'}
        ]
    },
    {
        'id': 'q16_children_planning',
        'text': 'I have adequately planned my children future for his school | University | Career Start Up.',
        'options': [
            {'value': 5, 'label': '100% adequate savings in place for all 3 Aspects'},
            {'value': 4, 'label': '80% savings in place for all 3 Aspects'},
            {'value': 3, 'label': '50% savings in place for all 3 Aspects'},
            {'value': 2, 'label': 'Adhoc plan in place for all 3 Aspects'},
            {'value': 1, 'label': 'No Plan in place'}
        ]
    }
]

# Sample recommendation templates
RECOMMENDATION_TEMPLATES = [
    {
        'id': 'budgeting_basic',
        'category': 'budgeting',
        'title': 'Improve Budget Management',
        'text': 'Create a detailed monthly budget to track your income and expenses. Use money management apps or simple spreadsheets to monitor your daily spending.'
    },
    {
        'id': 'savings_emergency',
        'category': 'savings',
        'title': 'Build Emergency Fund',
        'text': 'It\'s crucial to have an emergency fund that covers your expenses for 3-6 months. Start by saving a small amount monthly until you reach your target.'
    },
    {
        'id': 'debt_management',
        'category': 'debt_management',
        'title': 'Manage Debt Effectively',
        'text': 'If you have multiple debts, focus on paying off high-interest debts first. Consider debt consolidation if it reduces your overall interest payments.'
    },
    {
        'id': 'investment_basic',
        'category': 'investment',
        'title': 'Start Investing',
        'text': 'Begin your investment journey by learning the basics first. Consider investing in index funds or diversified funds as a safe starting point.'
    },
    {
        'id': 'retirement_planning',
        'category': 'retirement_planning',
        'title': 'Plan for Retirement',
        'text': 'It\'s never too late to start planning for retirement. Save at least 10-15% of your income for retirement and take advantage of any employer retirement programs.'
    }
]


async def populate_ui_elements(service: LocalizationService) -> int:
    """Populate all UI elements into the database."""
    print("Populating UI elements...")
    count = 0
    
    for content_id, text in UI_ELEMENTS.items():
        try:
            await service.create_localized_content(
                content_type="ui",
                content_id=content_id,
                language="en",
                text=text,
                version="1.0"
            )
            count += 1
            if count % 10 == 0:
                print(f"  Created {count} UI elements...")
        except Exception as e:
            print(f"  Error creating UI element {content_id}: {str(e)}")
    
    print(f"✓ Created {count} UI elements")
    return count


async def populate_questions(service: LocalizationService) -> int:
    """Populate all survey questions into the database."""
    print("Populating survey questions...")
    count = 0
    
    for question in SURVEY_QUESTIONS:
        try:
            await service.create_localized_content(
                content_type="question",
                content_id=question['id'],
                language="en",
                text=question['text'],
                options=question['options'],
                version="1.0"
            )
            count += 1
            print(f"  Created question: {question['id']}")
        except Exception as e:
            print(f"  Error creating question {question['id']}: {str(e)}")
    
    print(f"✓ Created {count} questions")
    return count


async def populate_recommendations(service: LocalizationService) -> int:
    """Populate recommendation templates into the database."""
    print("Populating recommendation templates...")
    count = 0
    
    for rec in RECOMMENDATION_TEMPLATES:
        try:
            await service.create_localized_content(
                content_type="recommendation",
                content_id=rec['id'],
                language="en",
                text=rec['text'],
                title=rec['title'],
                extra_data={'category': rec['category']},
                version="1.0"
            )
            count += 1
            print(f"  Created recommendation: {rec['id']}")
        except Exception as e:
            print(f"  Error creating recommendation {rec['id']}: {str(e)}")
    
    print(f"✓ Created {count} recommendations")
    return count


async def check_existing_content(db: Session) -> Dict[str, int]:
    """Check what content already exists in the database."""
    print("Checking existing content...")
    
    ui_count = db.query(LocalizedContent).filter(
        LocalizedContent.content_type == "ui",
        LocalizedContent.language == "en"
    ).count()
    
    question_count = db.query(LocalizedContent).filter(
        LocalizedContent.content_type == "question",
        LocalizedContent.language == "en"
    ).count()
    
    rec_count = db.query(LocalizedContent).filter(
        LocalizedContent.content_type == "recommendation",
        LocalizedContent.language == "en"
    ).count()
    
    print(f"  Existing UI elements: {ui_count}")
    print(f"  Existing questions: {question_count}")
    print(f"  Existing recommendations: {rec_count}")
    
    return {
        'ui': ui_count,
        'questions': question_count,
        'recommendations': rec_count
    }


async def main():
    """Main function to populate all content."""
    print("=== Populating All Frontend Content to Database ===")
    print("This will create English content that admins can then translate through the admin interface.\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)
        
        # Check existing content
        existing = await check_existing_content(db)
        
        # Ask for confirmation if content exists
        if any(existing.values()):
            print(f"\nWarning: Some content already exists in the database.")
            print("This script will update existing content with the same content_id and language.")
            response = input("Do you want to continue? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return
        
        # Create localization service
        service = LocalizationService(db)
        
        # Populate all content types
        print(f"\nStarting content population...")
        
        ui_count = await populate_ui_elements(service)
        question_count = await populate_questions(service)
        rec_count = await populate_recommendations(service)
        
        total_count = ui_count + question_count + rec_count
        
        print(f"\n🎉 Successfully populated {total_count} content items!")
        print(f"  - UI Elements: {ui_count}")
        print(f"  - Questions: {question_count}")
        print(f"  - Recommendations: {rec_count}")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Access the admin dashboard at /admin")
        print(f"2. Go to 'Localization Management'")
        print(f"3. Create Arabic translations for the content")
        print(f"4. Use the translation workflows for bulk operations")
        print(f"5. Test the translations on the frontend")
        
        print(f"\n✨ All content is now available for translation management!")
        
    except Exception as e:
        print(f"\n❌ Error during population: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())