#!/usr/bin/env python3
"""
Update homepage translations with new content.
This script adds the missing translation keys for the homepage.
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.localization.service import LocalizationService


# New UI elements for homepage
NEW_UI_ELEMENTS = {
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
}

# Arabic translations for new elements
ARABIC_UI_ELEMENTS = {
    'transparent_scoring_description': 'افهم بالضبط كيف يتم حساب درجتك مع شرح واضح لكل عامل.',
    'privacy_protected_description': 'يتم التعامل مع بياناتك وفقاً لقانون حماية البيانات الإماراتي مع إدارة كاملة للموافقة.',
    'personalized_insights_description': 'احصل على توصيات مخصصة بناءً على وضعك المالي وأهدافك الفريدة.',
    'progress_tracking_description': 'احفظ نتائجك بمجرد البريد الإلكتروني وتاريخ الميلاد. لا حاجة لكلمات مرور لتتبع تقدمك عبر الزمن.',
    'about_financial_health_assessment': 'حول تقييم الصحة المالية',
    'science_based_methodology_description': 'يستخدم تقييمنا مقاييس العافية المالية المثبتة والمكيفة خصيصاً لسكان دولة الإمارات. يقيم نظام التسجيل خمسة أركان رئيسية للصحة المالية.',
    'budgeting_expense_management': 'إدارة الميزانية والنفقات',
    'savings_emergency_funds': 'المدخرات وصناديق الطوارئ',
    'financial_planning_goals': 'التخطيط المالي والأهداف',
    'investment_wealth_building': 'الاستثمار وبناء الثروة',
    'uae_specific_insights_description': 'مصمم خصيصاً للسوق الإماراتي مع توصيات محلية تأخذ في الاعتبار المنتجات المالية واللوائح والعوامل الثقافية الخاصة بالإمارات.',
    'uae_banking_products_services': 'المنتجات والخدمات المصرفية الإماراتية',
    'adcb_emirates_nbd_partnerships': 'شراكات بنك أبوظبي التجاري وبنك الإمارات دبي الوطني',
    'sharia_compliant_options': 'خيارات متوافقة مع الشريعة',
    'expat_specific_considerations': 'اعتبارات خاصة بالمغتربين',
    'local_investment_opportunities': 'فرص الاستثمار المحلية',
    'save_results_no_passwords': 'احفظ نتائجك بمجرد بريدك الإلكتروني وتاريخ ميلادك - لا حاجة لكلمات مرور!',
    'continue_your_journey': 'تابع رحلتك'
}


async def add_english_elements(service: LocalizationService) -> int:
    """Add new English UI elements."""
    print("Adding new English UI elements...")
    count = 0
    
    for content_id, text in NEW_UI_ELEMENTS.items():
        try:
            await service.create_localized_content(
                content_type="ui",
                content_id=content_id,
                language="en",
                text=text,
                version="1.0"
            )
            count += 1
            print(f"  Added: {content_id}")
        except Exception as e:
            print(f"  Error adding {content_id}: {str(e)}")
    
    print(f"✓ Added {count} English UI elements")
    return count


async def add_arabic_elements(service: LocalizationService) -> int:
    """Add Arabic translations for new UI elements."""
    print("Adding Arabic translations...")
    count = 0
    
    for content_id, text in ARABIC_UI_ELEMENTS.items():
        try:
            await service.create_localized_content(
                content_type="ui",
                content_id=content_id,
                language="ar",
                text=text,
                version="1.0"
            )
            count += 1
            print(f"  Added Arabic: {content_id}")
        except Exception as e:
            print(f"  Error adding Arabic {content_id}: {str(e)}")
    
    print(f"✓ Added {count} Arabic UI elements")
    return count


async def test_homepage_translations(service: LocalizationService):
    """Test that homepage translations are working."""
    print("\nTesting homepage translations...")
    
    # Test key homepage elements
    test_keys = [
        'financial_health_assessment',
        'trusted_uae_institution', 
        'transparent_scoring_description',
        'about_financial_health_assessment',
        'ready_to_improve'
    ]
    
    # Test English
    en_translations = await service.get_ui_content_by_language(test_keys, "en")
    print(f"English translations found: {len(en_translations)}/{len(test_keys)}")
    
    # Test Arabic
    ar_translations = await service.get_ui_content_by_language(test_keys, "ar")
    print(f"Arabic translations found: {len(ar_translations)}/{len(test_keys)}")
    
    # Show sample translations
    if 'financial_health_assessment' in ar_translations:
        print(f"Sample Arabic: {ar_translations['financial_health_assessment']}")
    
    print("✓ Homepage translation test completed!")


async def main():
    """Main function to update homepage translations."""
    print("=== Updating Homepage Translations ===")
    print("Adding missing translation keys for the homepage...\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)
        
        # Create localization service
        service = LocalizationService(db)
        
        # Add new translations
        en_count = await add_english_elements(service)
        ar_count = await add_arabic_elements(service)
        
        total_count = en_count + ar_count
        
        print(f"\n🎉 Successfully added {total_count} translation items!")
        print(f"  - English elements: {en_count}")
        print(f"  - Arabic elements: {ar_count}")
        
        # Test the translations
        await test_homepage_translations(service)
        
        print(f"\n📋 Next Steps:")
        print(f"1. Refresh your homepage")
        print(f"2. Test language switching")
        print(f"3. Check that all text is now translatable")
        print(f"4. Access admin interface to manage more translations")
        
        print(f"\n✨ Homepage should now be fully translatable!")
        
    except Exception as e:
        print(f"\n❌ Error updating homepage translations: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())