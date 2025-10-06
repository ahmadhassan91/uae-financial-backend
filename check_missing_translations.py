#!/usr/bin/env python3
"""Check what translations are missing from the database."""

from app.database import get_db
from app.models import LocalizedContent
from sqlalchemy.orm import Session

def check_missing_translations():
    # Get database session
    db = next(get_db())

    try:
        # Check what UI translations exist
        ui_content = db.query(LocalizedContent).filter(
            LocalizedContent.content_type == 'ui',
            LocalizedContent.is_active == True
        ).all()

        print('=== EXISTING UI TRANSLATIONS ===')
        en_keys = set()
        ar_keys = set()

        for item in ui_content:
            if item.language == 'en':
                en_keys.add(item.content_id)
            elif item.language == 'ar':
                ar_keys.add(item.content_id)

        print(f'English UI keys: {len(en_keys)}')
        print(f'Arabic UI keys: {len(ar_keys)}')

        # Find missing Arabic translations
        missing_ar = en_keys - ar_keys
        print(f'Missing Arabic translations: {len(missing_ar)}')
        if missing_ar:
            print('Missing keys:', sorted(list(missing_ar))[:20])  # Show first 20

        # Find keys that exist in Arabic but not English
        extra_ar = ar_keys - en_keys
        print(f'Arabic-only keys: {len(extra_ar)}')
        if extra_ar:
            print('Arabic-only keys:', sorted(list(extra_ar))[:10])

        # Check homepage specific keys
        homepage_keys = [
            'financial_health_assessment', 'trusted_uae_institution', 'get_personalized_insights',
            'transparent_scoring', 'transparent_scoring_description', 'privacy_protected', 
            'privacy_protected_description', 'personalized_insights', 'personalized_insights_description',
            'progress_tracking', 'progress_tracking_description', 'about_financial_health_assessment',
            'science_based_methodology', 'science_based_methodology_description',
            'budgeting_expense_management', 'savings_emergency_funds', 'debt_management',
            'financial_planning_goals', 'investment_wealth_building', 'uae_specific_insights',
            'uae_specific_insights_description', 'uae_banking_products_services',
            'adcb_emirates_nbd_partnerships', 'sharia_compliant_options', 'expat_specific_considerations',
            'local_investment_opportunities', 'ready_to_improve', 'join_thousands',
            'save_results_no_passwords', 'continue_your_journey', 'begin_assessment_now'
        ]

        print('\n=== HOMEPAGE TRANSLATION STATUS ===')
        for key in homepage_keys:
            en_exists = key in en_keys
            ar_exists = key in ar_keys
            status = "✅" if (en_exists and ar_exists) else "❌" if not ar_exists else "⚠️"
            print(f'{status} {key}: EN={en_exists}, AR={ar_exists}')

        # Check results page keys
        results_keys = [
            'your_results', 'financial_health_score', 'overall_score', 'pillar_breakdown',
            'detailed_recommendations', 'action_plan', 'next_steps', 'download_report',
            'email_report', 'share_results', 'excellent', 'good', 'fair', 'needs_improvement',
            'poor', 'at_risk', 'budgeting', 'savings', 'debt_management', 'financial_planning',
            'investment_knowledge', 'income_stream', 'monthly_expenses', 'savings_habit',
            'retirement_planning', 'protection', 'future_planning'
        ]

        print('\n=== RESULTS PAGE TRANSLATION STATUS ===')
        for key in results_keys:
            en_exists = key in en_keys
            ar_exists = key in ar_keys
            status = "✅" if (en_exists and ar_exists) else "❌" if not ar_exists else "⚠️"
            print(f'{status} {key}: EN={en_exists}, AR={ar_exists}')

    finally:
        db.close()

if __name__ == "__main__":
    check_missing_translations()