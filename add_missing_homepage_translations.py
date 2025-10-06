#!/usr/bin/env python3
"""Add missing homepage and results page translations to the database."""

import asyncio
from app.database import get_db
from app.localization.service import LocalizationService

# Homepage translations that are missing
HOMEPAGE_TRANSLATIONS = {
    # Homepage content
    'financial_health_assessment': 'تقييم الصحة المالية',
    'trusted_uae_institution': 'مؤسسة مالية إماراتية موثوقة تقدم تقييماً شفافاً ومبنياً على العلم للعافية المالية.',
    'get_personalized_insights': 'احصل على رؤى مخصصة لتعزيز مستقبلك المالي.',
    
    # Features
    'transparent_scoring': 'تسجيل شفاف',
    'transparent_scoring_description': 'افهم بالضبط كيف يتم حساب درجتك مع شرح واضح لكل عامل.',
    'privacy_protected': 'حماية الخصوصية',
    'privacy_protected_description': 'يتم التعامل مع بياناتك وفقاً لقانون حماية البيانات الإماراتي مع إدارة كاملة للموافقة.',
    'personalized_insights': 'رؤى مخصصة',
    'personalized_insights_description': 'احصل على توصيات مخصصة بناءً على وضعك المالي وأهدافك الفريدة.',
    'progress_tracking': 'تتبع التقدم',
    'progress_tracking_description': 'احفظ نتائجك بمجرد البريد الإلكتروني وتاريخ الميلاد. لا حاجة لكلمات مرور لتتبع تقدمك عبر الزمن.',
    
    # About section
    'about_financial_health_assessment': 'حول تقييم الصحة المالية',
    'science_based_methodology': 'منهجية علمية',
    'science_based_methodology_description': 'يستخدم تقييمنا مقاييس العافية المالية المثبتة والمكيفة خصيصاً لسكان دولة الإمارات. يقيم نظام التسجيل خمسة أركان رئيسية للصحة المالية.',
    'budgeting_expense_management': 'إدارة الميزانية والنفقات',
    'savings_emergency_funds': 'المدخرات وصناديق الطوارئ',
    'debt_management': 'إدارة الديون',
    'financial_planning_goals': 'التخطيط المالي والأهداف',
    'investment_wealth_building': 'الاستثمار وبناء الثروة',
    
    'uae_specific_insights': 'رؤى خاصة بدولة الإمارات',
    'uae_specific_insights_description': 'مصمم خصيصاً للسوق الإماراتي مع توصيات محلية تأخذ في الاعتبار المنتجات المالية واللوائح والعوامل الثقافية الخاصة بالإمارات.',
    'uae_banking_products_services': 'المنتجات والخدمات المصرفية الإماراتية',
    'adcb_emirates_nbd_partnerships': 'شراكات بنك أبوظبي التجاري وبنك الإمارات دبي الوطني',
    'sharia_compliant_options': 'خيارات متوافقة مع الشريعة',
    'expat_specific_considerations': 'اعتبارات خاصة بالمغتربين',
    'local_investment_opportunities': 'فرص الاستثمار المحلية',
    
    # CTA section
    'ready_to_improve': 'هل أنت مستعد لتحسين صحتك المالية؟',
    'join_thousands': 'انضم إلى آلاف المقيمين في دولة الإمارات الذين عززوا مستقبلهم المالي من خلال تقييمنا الشامل.',
    'save_results_no_passwords': 'احفظ نتائجك بمجرد بريدك الإلكتروني وتاريخ ميلادك - لا حاجة لكلمات مرور!',
    'continue_your_journey': 'تابع رحلتك',
    'begin_assessment_now': 'ابدأ التقييم الآن',
}

# Results page translations
RESULTS_TRANSLATIONS = {
    'your_results': 'نتائجك',
    'financial_health_score': 'درجة الصحة المالية',
    'overall_score': 'النتيجة الإجمالية',
    'pillar_breakdown': 'تفصيل الأركان',
    'detailed_recommendations': 'توصيات مفصلة',
    'action_plan': 'خطة العمل',
    'next_steps': 'الخطوات التالية',
    'download_report': 'تحميل التقرير',
    'email_report': 'إرسال التقرير بالبريد الإلكتروني',
    'share_results': 'مشاركة النتائج',
    'generate_report': 'إنشاء التقرير',
    'understanding_your_score': 'فهم درجتك',
    'score_ranges': 'نطاقات الدرجات',
    'save_your_results': 'احفظ نتائجك',
    'create_account': 'إنشاء حساب',
    'view_score_history': 'عرض تاريخ النتائج',
    'retake_assessment': 'إعادة التقييم',
    'personalized_recommendations': 'توصيات مخصصة',
    'educational_guidance': 'إرشادات تعليمية',
    'financial_pillar_scores': 'درجات الأركان المالية',
    'performance_across_areas': 'أداؤك عبر المجالات الرئيسية',
    'no_results_available': 'لا توجد نتائج متاحة',
    'complete_assessment_first': 'تحتاج إلى إكمال تقييم الصحة المالية أولاً لرؤية نتائجك.',
    'error_loading_results': 'خطأ في تحميل النتائج',
    'unable_to_load_score': 'غير قادر على تحميل نتائج درجتك. يرجى المحاولة مرة أخرى.',
    
    # Score levels and descriptions
    'excellent': 'ممتاز',
    'good': 'جيد',
    'fair': 'مقبول',
    'needs_improvement': 'يحتاج تحسين',
    'poor': 'ضعيف',
    'at_risk': 'في خطر',
    
    # Pillar names
    'budgeting': 'إدارة الميزانية',
    'savings': 'الادخار',
    'investment_knowledge': 'المعرفة الاستثمارية',
    'income_stream': 'مصدر الدخل',
    'monthly_expenses': 'إدارة النفقات الشهرية',
    'savings_habit': 'عادة الادخار',
    'retirement_planning': 'التخطيط للتقاعد',
    'protection': 'حماية الأصول والأحباء',
    'future_planning': 'التخطيط للمستقبل والأشقاء',
    
    # Score interpretation descriptions
    'focus_on_building_basic_habits': 'ركز على بناء العادات المالية الأساسية',
    'good_foundation_room_for_growth': 'أساس جيد، مجال للنمو',
    'strong_financial_health': 'صحة مالية قوية',
    'outstanding_financial_wellness': 'عافية مالية متميزة',
    
    # Educational disclaimer
    'educational_content_only': 'هذا محتوى تعليمي فقط ولا يشكل نصيحة مالية.',
    'consult_qualified_professionals': 'استشر المهنيين المؤهلين للحصول على إرشادات مخصصة.',
    
    # Registration prompts
    'track_progress_download_reports': 'تتبع تقدمك، وحمل التقارير، والوصول إلى تاريخ تقييماتك.',
    'personalized_recommendations_generated': 'سيتم إنشاء توصيات مخصصة بناءً على نتائج تقييمك.',
    'detailed_breakdown_available': 'سيكون التفصيل المفصل متاحاً بعد إكمال التقييم.',
}

# Additional UI translations
ADDITIONAL_UI_TRANSLATIONS = {
    'welcome_back': 'مرحباً بعودتك!',
    'sign_out': 'تسجيل الخروج',
    'access_previous_results': 'الوصول إلى النتائج السابقة',
    'view_previous_results': 'عرض النتائج السابقة',
    'admin_dashboard': 'لوحة الإدارة',
    'start_assessment': 'ابدأ التقييم',
    'go_to_home': 'اذهب إلى الصفحة الرئيسية',
    'home': 'الرئيسية',
}

async def add_missing_translations():
    """Add missing translations to the database."""
    db = next(get_db())
    service = LocalizationService(db)
    
    try:
        # Combine all translations
        all_translations = {
            **HOMEPAGE_TRANSLATIONS,
            **RESULTS_TRANSLATIONS,
            **ADDITIONAL_UI_TRANSLATIONS
        }
        
        print(f"Adding {len(all_translations)} Arabic translations...")
        
        added_count = 0
        updated_count = 0
        
        for key, arabic_text in all_translations.items():
            try:
                # Create Arabic translation
                result = await service.create_localized_content(
                    content_type="ui",
                    content_id=key,
                    language="ar",
                    text=arabic_text,
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
        print(f"Total processed: {len(all_translations)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(add_missing_translations())