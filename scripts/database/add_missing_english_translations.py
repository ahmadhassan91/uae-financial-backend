#!/usr/bin/env python3
"""Add missing English translations to the database."""

import asyncio
from app.database import get_db
from app.localization.service import LocalizationService

# English translations that might be missing
ENGLISH_TRANSLATIONS = {
    # Homepage content
    'financial_health_assessment': 'Financial Health Assessment',
    'trusted_uae_institution': 'A trusted UAE financial institution providing transparent, science-based financial wellness assessment.',
    'get_personalized_insights': 'Get personalized insights to strengthen your financial future.',
    
    # Features
    'transparent_scoring': 'Transparent Scoring',
    'transparent_scoring_description': 'Understand exactly how your score is calculated with clear explanations for each factor.',
    'privacy_protected': 'Privacy Protected',
    'privacy_protected_description': 'Your data is handled according to UAE PDPL regulations with full consent management.',
    'personalized_insights': 'Personalized Insights',
    'personalized_insights_description': 'Receive tailored recommendations based on your unique financial situation and goals.',
    'progress_tracking': 'Progress Tracking',
    'progress_tracking_description': 'Save your results with just email and date of birth. No passwords needed to track your progress over time.',
    
    # About section
    'about_financial_health_assessment': 'About Financial Health Assessment',
    'science_based_methodology': 'Science-Based Methodology',
    'science_based_methodology_description': 'Our assessment uses proven financial wellness metrics adapted specifically for UAE residents. The scoring system evaluates five key pillars of financial health.',
    'budgeting_expense_management': 'Budgeting & Expense Management',
    'savings_emergency_funds': 'Savings & Emergency Funds',
    'debt_management': 'Debt Management',
    'financial_planning_goals': 'Financial Planning & Goals',
    'investment_wealth_building': 'Investment & Wealth Building',
    
    'uae_specific_insights': 'UAE-Specific Insights',
    'uae_specific_insights_description': 'Tailored for the UAE market with localized recommendations that consider Emirates-specific financial products, regulations, and cultural factors.',
    'uae_banking_products_services': 'UAE banking products & services',
    'adcb_emirates_nbd_partnerships': 'ADCB & Emirates NBD partnerships',
    'sharia_compliant_options': 'Sharia-compliant options',
    'expat_specific_considerations': 'Expat-specific considerations',
    'local_investment_opportunities': 'Local investment opportunities',
    
    # CTA section
    'ready_to_improve': 'Ready to Improve Your Financial Health?',
    'join_thousands': 'Join thousands of UAE residents who have strengthened their financial future with our comprehensive assessment.',
    'save_results_no_passwords': 'Save your results with just your email and date of birth - no passwords required!',
    'continue_your_journey': 'Continue Your Journey',
    'begin_assessment_now': 'Begin Assessment Now',
    
    # Results page translations
    'your_results': 'Your Results',
    'financial_health_score': 'Financial Health Score',
    'overall_score': 'Overall Score',
    'pillar_breakdown': 'Pillar Breakdown',
    'detailed_recommendations': 'Detailed Recommendations',
    'action_plan': 'Action Plan',
    'next_steps': 'Next Steps',
    'download_report': 'Download Report',
    'email_report': 'Email Report',
    'share_results': 'Share Results',
    'generate_report': 'Generate Report',
    'understanding_your_score': 'Understanding Your Score',
    'score_ranges': 'Score Ranges',
    'save_your_results': 'Save Your Results',
    'create_account': 'Create Account',
    'view_score_history': 'View Score History',
    'retake_assessment': 'Retake Assessment',
    'personalized_recommendations': 'Personalized Recommendations',
    'educational_guidance': 'Educational guidance to improve your financial health',
    'financial_pillar_scores': 'Financial Pillar Scores',
    'performance_across_areas': 'Your performance across key areas of financial health',
    'no_results_available': 'No Results Available',
    'complete_assessment_first': 'You need to complete the financial health assessment first to see your results.',
    'error_loading_results': 'Error Loading Results',
    'unable_to_load_score': 'Unable to load your score results. Please try the assessment again.',
    
    # Score levels and descriptions
    'excellent': 'Excellent',
    'good': 'Good',
    'fair': 'Fair',
    'needs_improvement': 'Needs Improvement',
    'poor': 'Poor',
    'at_risk': 'At Risk',
    
    # Pillar names
    'budgeting': 'Budgeting',
    'savings': 'Savings',
    'investment_knowledge': 'Investment Knowledge',
    'income_stream': 'Income Stream',
    'monthly_expenses': 'Monthly Expenses Management',
    'savings_habit': 'Savings Habit',
    'retirement_planning': 'Retirement Planning',
    'protection': 'Protecting Your Assets & Loved Ones',
    'future_planning': 'Planning for Your Future & Siblings',
    
    # Score interpretation descriptions
    'focus_on_building_basic_habits': 'Focus on building basic financial habits',
    'good_foundation_room_for_growth': 'Good foundation, room for growth',
    'strong_financial_health': 'Strong financial health',
    'outstanding_financial_wellness': 'Outstanding financial wellness',
    
    # Educational disclaimer
    'educational_content_only': 'This is educational content only and does not constitute financial advice.',
    'consult_qualified_professionals': 'Consult qualified professionals for personalized guidance.',
    
    # Registration prompts
    'track_progress_download_reports': 'Track your progress, download reports, and access your assessment history.',
    'personalized_recommendations_generated': 'Personalized recommendations will be generated based on your assessment results.',
    'detailed_breakdown_available': 'Detailed pillar breakdown will be available after completing the assessment.',
    
    # Additional UI translations
    'welcome_back': 'Welcome back!',
    'sign_out': 'Sign Out',
    'access_previous_results': 'Access Previous Results',
    'view_previous_results': 'View Previous Results',
    'admin_dashboard': 'Admin Dashboard',
    'start_assessment': 'Start Assessment',
    'go_to_home': 'Go to Home',
    'home': 'Home',
}

async def add_missing_english_translations():
    """Add missing English translations to the database."""
    db = next(get_db())
    service = LocalizationService(db)
    
    try:
        print(f"Adding {len(ENGLISH_TRANSLATIONS)} English translations...")
        
        added_count = 0
        updated_count = 0
        
        for key, english_text in ENGLISH_TRANSLATIONS.items():
            try:
                # Create English translation
                result = await service.create_localized_content(
                    content_type="ui",
                    content_id=key,
                    language="en",
                    text=english_text,
                    version="1.0"
                )
                
                if result:
                    added_count += 1
                    print(f"✅ Added: {key}")
                else:
                    updated_count += 1
                    print(f"🔄 Updated: {key}")
                    
            except Exception as e:
                print(f"❌ Error with {key}: {str(e)}")
        
        print(f"\n=== SUMMARY ===")
        print(f"Added: {added_count}")
        print(f"Updated: {updated_count}")
        print(f"Total processed: {len(ENGLISH_TRANSLATIONS)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(add_missing_english_translations())