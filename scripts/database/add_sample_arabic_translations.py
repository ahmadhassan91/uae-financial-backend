#!/usr/bin/env python3
"""
Add sample Arabic translations for key content items.
This demonstrates how translations work and provides a starting point.
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.localization.service import LocalizationService


# Sample Arabic translations for key UI elements
ARABIC_UI_TRANSLATIONS = {
    'welcome_message': 'مرحباً بك في تقييم الصحة المالية',
    'start_survey': 'ابدأ التقييم',
    'next_question': 'السؤال التالي',
    'previous_question': 'السؤال السابق',
    'submit_survey': 'إرسال التقييم',
    'your_results': 'نتائجك',
    'download_pdf': 'تحميل التقرير',
    'send_email': 'إرسال بالبريد الإلكتروني',
    'register_account': 'إنشاء حساب',
    'language_selector': 'اختر اللغة',
    'financial_health_score': 'درجة الصحة المالية',
    'recommendations': 'التوصيات',
    'budgeting': 'إدارة الميزانية',
    'savings': 'الادخار',
    'debt_management': 'إدارة الديون',
    'financial_planning': 'التخطيط المالي',
    'investment_knowledge': 'المعرفة الاستثمارية',
    'excellent': 'ممتاز',
    'good': 'جيد',
    'fair': 'مقبول',
    'poor': 'ضعيف',
    'personal_information': 'المعلومات الشخصية',
    'first_name': 'الاسم الأول',
    'last_name': 'اسم العائلة',
    'age': 'العمر',
    'gender': 'الجنس',
    'male': 'ذكر',
    'female': 'أنثى',
    'nationality': 'الجنسية',
    'emirate': 'الإمارة',
    'employment_status': 'الحالة الوظيفية',
    'monthly_income': 'الدخل الشهري',
    'household_size': 'عدد أفراد الأسرة',
    'children': 'الأطفال',
    'yes': 'نعم',
    'no': 'لا',
    'email': 'البريد الإلكتروني',
    'phone_number': 'رقم الهاتف',
    'save': 'حفظ',
    'cancel': 'إلغاء',
    'edit': 'تعديل',
    'delete': 'حذف',
    'confirm': 'تأكيد',
    'loading': 'جاري التحميل...',
    'error': 'خطأ',
    'success': 'نجح',
    'warning': 'تحذير',
    'info': 'معلومات',
    'continue': 'متابعة',
    'back': 'رجوع',
    'complete': 'إكمال',
    
    # Landing Page Extended Content
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

# Sample Arabic translations for key questions
ARABIC_QUESTIONS = {
    'q1_income_stability': {
        'text': 'دخلي مستقر ويمكن التنبؤ به كل شهر.',
        'options': [
            {'value': 5, 'label': 'أوافق بشدة'},
            {'value': 4, 'label': 'أوافق'},
            {'value': 3, 'label': 'محايد'},
            {'value': 2, 'label': 'لا أوافق'},
            {'value': 1, 'label': 'لا أوافق بشدة'}
        ]
    },
    'q2_income_sources': {
        'text': 'لدي أكثر من مصدر دخل واحد (مثل عمل جانبي، استثمارات).',
        'options': [
            {'value': 5, 'label': 'مصادر دخل متعددة ومستقرة'},
            {'value': 4, 'label': 'مصادر دخل متعددة وغير مستقرة'},
            {'value': 3, 'label': 'لدي دخل جانبي مستقر'},
            {'value': 2, 'label': 'دخل جانبي غير مستقر'},
            {'value': 1, 'label': 'راتبي فقط'}
        ]
    },
    'q3_living_expenses': {
        'text': 'يمكنني تغطية نفقات المعيشة الأساسية دون ضغط مالي.',
        'options': [
            {'value': 5, 'label': 'أوافق بشدة'},
            {'value': 4, 'label': 'أوافق'},
            {'value': 3, 'label': 'محايد'},
            {'value': 2, 'label': 'لا أوافق'},
            {'value': 1, 'label': 'لا أوافق بشدة'}
        ]
    },
    'q7_savings_rate': {
        'text': 'أدخر من دخلي كل شهر.',
        'options': [
            {'value': 5, 'label': '20% أو أكثر'},
            {'value': 4, 'label': 'أقل من 20%'},
            {'value': 3, 'label': 'أقل من 10%'},
            {'value': 2, 'label': '5% أو أقل'},
            {'value': 1, 'label': '0%'}
        ]
    },
    'q13_retirement_planning': {
        'text': 'لدي خطة ادخار للتقاعد أو صندوق معاشات لضمان دخل مستقر عند التقاعد.',
        'options': [
            {'value': 5, 'label': 'نعم - لقد ضمنت دخلاً مستقراً بالفعل'},
            {'value': 4, 'label': 'نعم - أنا واثق جداً من الحصول على دخل مستقر'},
            {'value': 3, 'label': 'نعم - أنا واثق إلى حد ما من الحصول على دخل مستقر'},
            {'value': 2, 'label': 'لا: أخطط للحصول على واحدة قريباً | مدخرات عشوائية'},
            {'value': 1, 'label': 'لا: ليس في الوقت الحالي'}
        ]
    }
}

# Sample Arabic recommendations
ARABIC_RECOMMENDATIONS = {
    'budgeting_basic': {
        'title': 'تحسين إدارة الميزانية',
        'text': 'أنشئ ميزانية شهرية مفصلة لتتبع دخلك ونفقاتك. استخدم تطبيقات إدارة المال أو جداول بيانات بسيطة لمراقبة إنفاقك اليومي.',
        'extra_data': {
            'action_steps': [
                'سجل جميع مصادر دخلك الشهري',
                'اكتب جميع نفقاتك الثابتة والمتغيرة',
                'حدد أولويات الإنفاق',
                'راجع ميزانيتك أسبوعياً'
            ],
            'cultural_note': 'يُنصح بتخصيص جزء من الدخل للزكاة والصدقات حسب التعاليم الإسلامية'
        }
    },
    'savings_emergency': {
        'title': 'بناء صندوق الطوارئ',
        'text': 'من المهم جداً أن يكون لديك صندوق طوارئ يغطي نفقاتك لمدة 3-6 أشهر. ابدأ بادخار مبلغ صغير شهرياً حتى تصل للهدف المطلوب.',
        'extra_data': {
            'action_steps': [
                'احسب نفقاتك الشهرية الأساسية',
                'اضرب هذا المبلغ في 6 أشهر',
                'ادخر 10-20% من راتبك شهرياً',
                'ضع المدخرات في حساب منفصل'
            ],
            'local_resources': [
                'حسابات الادخار في البنوك الإماراتية',
                'صناديق الاستثمار قصيرة المدى'
            ]
        }
    }
}


async def add_arabic_ui_translations(service: LocalizationService) -> int:
    """Add Arabic translations for UI elements."""
    print("Adding Arabic UI translations...")
    count = 0
    
    for content_id, text in ARABIC_UI_TRANSLATIONS.items():
        try:
            await service.create_localized_content(
                content_type="ui",
                content_id=content_id,
                language="ar",
                text=text,
                version="1.0"
            )
            count += 1
            if count % 10 == 0:
                print(f"  Added {count} Arabic UI translations...")
        except Exception as e:
            print(f"  Error adding UI translation {content_id}: {str(e)}")
    
    print(f"✓ Added {count} Arabic UI translations")
    return count


async def add_arabic_questions(service: LocalizationService) -> int:
    """Add Arabic translations for questions."""
    print("Adding Arabic question translations...")
    count = 0
    
    for question_id, question_data in ARABIC_QUESTIONS.items():
        try:
            await service.create_localized_content(
                content_type="question",
                content_id=question_id,
                language="ar",
                text=question_data['text'],
                options=question_data['options'],
                version="1.0"
            )
            count += 1
            print(f"  Added Arabic translation for: {question_id}")
        except Exception as e:
            print(f"  Error adding question translation {question_id}: {str(e)}")
    
    print(f"✓ Added {count} Arabic question translations")
    return count


async def add_arabic_recommendations(service: LocalizationService) -> int:
    """Add Arabic translations for recommendations."""
    print("Adding Arabic recommendation translations...")
    count = 0
    
    for rec_id, rec_data in ARABIC_RECOMMENDATIONS.items():
        try:
            await service.create_localized_content(
                content_type="recommendation",
                content_id=rec_id,
                language="ar",
                text=rec_data['text'],
                title=rec_data['title'],
                extra_data=rec_data.get('extra_data'),
                version="1.0"
            )
            count += 1
            print(f"  Added Arabic translation for: {rec_id}")
        except Exception as e:
            print(f"  Error adding recommendation translation {rec_id}: {str(e)}")
    
    print(f"✓ Added {count} Arabic recommendation translations")
    return count


async def test_arabic_translations(service: LocalizationService):
    """Test that Arabic translations work correctly."""
    print("\nTesting Arabic translations...")
    
    # Test UI translations
    ui_keys = ['welcome_message', 'start_survey', 'financial_health_score']
    translations = await service.get_ui_content_by_language(ui_keys, "ar")
    
    print("Sample Arabic UI translations:")
    for key in ui_keys:
        if key in translations:
            print(f"  {key}: {translations[key]}")
    
    # Test questions
    questions = await service.get_questions_by_language("ar")
    print(f"\nArabic questions available: {len(questions)}")
    
    if questions:
        sample_question = questions[0]
        print(f"Sample question: {sample_question.get('text', 'N/A')}")
    
    print("✓ Arabic translations are working!")


async def main():
    """Main function to add sample Arabic translations."""
    print("=== Adding Sample Arabic Translations ===")
    print("This will add Arabic translations for key content items.\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)
        
        # Create localization service
        service = LocalizationService(db)
        
        # Add Arabic translations
        print("Starting Arabic translation addition...")
        
        ui_count = await add_arabic_ui_translations(service)
        question_count = await add_arabic_questions(service)
        rec_count = await add_arabic_recommendations(service)
        
        total_count = ui_count + question_count + rec_count
        
        print(f"\n🎉 Successfully added {total_count} Arabic translations!")
        print(f"  - UI Elements: {ui_count}")
        print(f"  - Questions: {question_count}")
        print(f"  - Recommendations: {rec_count}")
        
        # Test the translations
        await test_arabic_translations(service)
        
        print(f"\n📋 Next Steps:")
        print(f"1. Access the admin dashboard at /admin")
        print(f"2. Go to 'Localization Management'")
        print(f"3. Filter by Language: Arabic to see all translations")
        print(f"4. Test language switching on the frontend")
        print(f"5. Add more Arabic translations as needed")
        
        print(f"\n✨ Arabic translations are now available!")
        
    except Exception as e:
        print(f"\n❌ Error adding Arabic translations: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())