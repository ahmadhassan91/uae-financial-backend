#!/usr/bin/env python3
"""
Add missing translations for assessment questions and results page
This script will add any missing translations that are needed for complete coverage
"""

import os
import sys
import psycopg2
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def add_missing_assessment_translations():
    """Add missing translations for assessment questions and results"""
    print("🔍 Adding Missing Assessment Translations")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="uae_financial_health",
            user="clustox1"
        )
        
        cursor = conn.cursor()
        
        # Additional assessment-related translations that might be missing
        additional_translations = [
            # Assessment flow
            {
                'content_type': 'ui',
                'content_id': 'assessment_progress',
                'en': 'Assessment Progress',
                'ar': 'تقدم التقييم'
            },
            {
                'content_type': 'ui',
                'content_id': 'question_of',
                'en': 'Question {{current}} of {{total}}',
                'ar': 'السؤال {{current}} من {{total}}'
            },
            {
                'content_type': 'ui',
                'content_id': 'assessment_complete',
                'en': 'Assessment Complete',
                'ar': 'اكتمل التقييم'
            },
            {
                'content_type': 'ui',
                'content_id': 'calculating_results',
                'en': 'Calculating your results...',
                'ar': 'جاري حساب النتائج...'
            },
            
            # Results page
            {
                'content_type': 'ui',
                'content_id': 'your_score',
                'en': 'Your Score',
                'ar': 'درجتك'
            },
            {
                'content_type': 'ui',
                'content_id': 'score_breakdown',
                'en': 'Score Breakdown',
                'ar': 'تفصيل الدرجات'
            },
            {
                'content_type': 'ui',
                'content_id': 'improvement_areas',
                'en': 'Areas for Improvement',
                'ar': 'مجالات التحسين'
            },
            {
                'content_type': 'ui',
                'content_id': 'strengths',
                'en': 'Your Strengths',
                'ar': 'نقاط قوتك'
            },
            {
                'content_type': 'ui',
                'content_id': 'next_steps_title',
                'en': 'Recommended Next Steps',
                'ar': 'الخطوات التالية الموصى بها'
            },
            
            # Score interpretations
            {
                'content_type': 'ui',
                'content_id': 'score_excellent_desc',
                'en': 'Outstanding financial health! You have strong financial habits and planning.',
                'ar': 'صحة مالية ممتازة! لديك عادات مالية قوية وتخطيط جيد.'
            },
            {
                'content_type': 'ui',
                'content_id': 'score_good_desc',
                'en': 'Good financial health with room for improvement in some areas.',
                'ar': 'صحة مالية جيدة مع مجال للتحسين في بعض المناطق.'
            },
            {
                'content_type': 'ui',
                'content_id': 'score_fair_desc',
                'en': 'Fair financial health. Focus on building better financial habits.',
                'ar': 'صحة مالية مقبولة. ركز على بناء عادات مالية أفضل.'
            },
            {
                'content_type': 'ui',
                'content_id': 'score_poor_desc',
                'en': 'Your financial health needs attention. Consider seeking financial advice.',
                'ar': 'صحتك المالية تحتاج إلى اهتمام. فكر في طلب المشورة المالية.'
            },
            
            # Pillar descriptions
            {
                'content_type': 'ui',
                'content_id': 'budgeting_pillar_desc',
                'en': 'How well you manage your monthly income and expenses',
                'ar': 'مدى جودة إدارتك لدخلك ونفقاتك الشهرية'
            },
            {
                'content_type': 'ui',
                'content_id': 'savings_pillar_desc',
                'en': 'Your ability to save money and build emergency funds',
                'ar': 'قدرتك على توفير المال وبناء صناديق الطوارئ'
            },
            {
                'content_type': 'ui',
                'content_id': 'debt_pillar_desc',
                'en': 'How effectively you manage and reduce your debts',
                'ar': 'مدى فعالية إدارتك وتقليل ديونك'
            },
            {
                'content_type': 'ui',
                'content_id': 'planning_pillar_desc',
                'en': 'Your long-term financial planning and goal setting',
                'ar': 'تخطيطك المالي طويل المدى ووضع الأهداف'
            },
            {
                'content_type': 'ui',
                'content_id': 'investment_pillar_desc',
                'en': 'Your knowledge and experience with investments',
                'ar': 'معرفتك وخبرتك في الاستثمارات'
            },
            
            # Action items
            {
                'content_type': 'ui',
                'content_id': 'take_action',
                'en': 'Take Action',
                'ar': 'اتخذ إجراء'
            },
            {
                'content_type': 'ui',
                'content_id': 'learn_more',
                'en': 'Learn More',
                'ar': 'تعلم المزيد'
            },
            {
                'content_type': 'ui',
                'content_id': 'get_advice',
                'en': 'Get Professional Advice',
                'ar': 'احصل على مشورة مهنية'
            },
            
            # Report generation
            {
                'content_type': 'ui',
                'content_id': 'generating_pdf',
                'en': 'Generating PDF report...',
                'ar': 'جاري إنشاء تقرير PDF...'
            },
            {
                'content_type': 'ui',
                'content_id': 'report_ready',
                'en': 'Your report is ready!',
                'ar': 'تقريرك جاهز!'
            },
            {
                'content_type': 'ui',
                'content_id': 'email_sent',
                'en': 'Report sent to your email',
                'ar': 'تم إرسال التقرير إلى بريدك الإلكتروني'
            },
            
            # Additional question types
            {
                'content_type': 'ui',
                'content_id': 'multiple_choice',
                'en': 'Multiple Choice',
                'ar': 'اختيار متعدد'
            },
            {
                'content_type': 'ui',
                'content_id': 'select_one',
                'en': 'Select one option',
                'ar': 'اختر خياراً واحداً'
            },
            {
                'content_type': 'ui',
                'content_id': 'required_question',
                'en': 'This question is required',
                'ar': 'هذا السؤال مطلوب'
            },
            
            # Navigation
            {
                'content_type': 'ui',
                'content_id': 'go_back',
                'en': 'Go Back',
                'ar': 'العودة'
            },
            {
                'content_type': 'ui',
                'content_id': 'finish_assessment',
                'en': 'Finish Assessment',
                'ar': 'إنهاء التقييم'
            },
            {
                'content_type': 'ui',
                'content_id': 'restart_assessment',
                'en': 'Restart Assessment',
                'ar': 'إعادة بدء التقييم'
            }
        ]
        
        added_count = 0
        updated_count = 0
        
        for translation in additional_translations:
            content_type = translation['content_type']
            content_id = translation['content_id']
            
            # Add English translation
            cursor.execute("""
                SELECT id FROM localized_content 
                WHERE content_type = %s AND content_id = %s AND language = 'en'
            """, (content_type, content_id))
            
            if cursor.fetchone():
                # Update existing
                cursor.execute("""
                    UPDATE localized_content 
                    SET text = %s, updated_at = %s, is_active = true
                    WHERE content_type = %s AND content_id = %s AND language = 'en'
                """, (translation['en'], datetime.now(), content_type, content_id))
                updated_count += 1
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO localized_content 
                    (content_type, content_id, language, text, is_active, created_at, updated_at)
                    VALUES (%s, %s, 'en', %s, true, %s, %s)
                """, (content_type, content_id, translation['en'], datetime.now(), datetime.now()))
                added_count += 1
            
            # Add Arabic translation
            cursor.execute("""
                SELECT id FROM localized_content 
                WHERE content_type = %s AND content_id = %s AND language = 'ar'
            """, (content_type, content_id))
            
            if cursor.fetchone():
                # Update existing
                cursor.execute("""
                    UPDATE localized_content 
                    SET text = %s, updated_at = %s, is_active = true
                    WHERE content_type = %s AND content_id = %s AND language = 'ar'
                """, (translation['ar'], datetime.now(), content_type, content_id))
                updated_count += 1
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO localized_content 
                    (content_type, content_id, language, text, is_active, created_at, updated_at)
                    VALUES (%s, %s, 'ar', %s, true, %s, %s)
                """, (content_type, content_id, translation['ar'], datetime.now(), datetime.now()))
                added_count += 1
        
        conn.commit()
        
        print(f"✅ Added {added_count} new translations")
        print(f"✅ Updated {updated_count} existing translations")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding translations: {e}")
        return False

def verify_question_translations():
    """Verify all survey questions have translations"""
    print(f"\n🔍 Verifying Survey Question Translations")
    print("=" * 60)
    
    try:
        from app.surveys.question_definitions import SURVEY_QUESTIONS_V2
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="uae_financial_health",
            user="clustox1"
        )
        
        cursor = conn.cursor()
        
        missing_questions = []
        
        for question in SURVEY_QUESTIONS_V2:
            # Check if question has Arabic translation
            cursor.execute("""
                SELECT id FROM localized_content 
                WHERE content_type = 'question' AND content_id = %s AND language = 'ar'
            """, (question.id,))
            
            if not cursor.fetchone():
                missing_questions.append(question.id)
        
        if missing_questions:
            print(f"⚠️  Found {len(missing_questions)} questions without Arabic translations:")
            for qid in missing_questions[:5]:
                print(f"    - {qid}")
            if len(missing_questions) > 5:
                print(f"    ... and {len(missing_questions) - 5} more")
        else:
            print("✅ All survey questions have Arabic translations")
        
        cursor.close()
        conn.close()
        
        return len(missing_questions) == 0
        
    except Exception as e:
        print(f"❌ Error verifying questions: {e}")
        return False

def test_frontend_integration():
    """Test if frontend can access the translations"""
    print(f"\n🔗 Testing Frontend Integration")
    print("=" * 60)
    
    try:
        import requests
        
        # Test localization endpoints
        endpoints = [
            "http://localhost:8000/api/localization/languages",
            "http://localhost:8000/api/localization/questions/en",
            "http://localhost:8000/api/localization/questions/ar",
            "http://localhost:8000/api/localization/ui/en",
            "http://localhost:8000/api/localization/ui/ar"
        ]
        
        results = []
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, (list, dict)) else 0
                    results.append(f"✅ {endpoint.split('/')[-1]}: {count} items")
                else:
                    results.append(f"❌ {endpoint.split('/')[-1]}: Status {response.status_code}")
            except Exception as e:
                results.append(f"❌ {endpoint.split('/')[-1]}: {str(e)}")
        
        for result in results:
            print(f"  {result}")
        
        return all("✅" in result for result in results)
        
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def main():
    """Main function to add missing translations"""
    print("🚀 Adding Missing Assessment & Results Translations")
    print("=" * 60)
    
    # Step 1: Add missing translations
    translations_added = add_missing_assessment_translations()
    
    # Step 2: Verify question translations
    questions_verified = verify_question_translations()
    
    # Step 3: Test frontend integration
    integration_working = test_frontend_integration()
    
    print(f"\n" + "=" * 60)
    print("📊 TRANSLATION UPDATE SUMMARY")
    print("=" * 60)
    
    print(f"Additional Translations: {'✅ ADDED' if translations_added else '❌ FAILED'}")
    print(f"Question Translations: {'✅ COMPLETE' if questions_verified else '⚠️ MISSING'}")
    print(f"Frontend Integration: {'✅ WORKING' if integration_working else '❌ FAILED'}")
    
    if translations_added and questions_verified and integration_working:
        print(f"\n🎉 ALL TRANSLATIONS READY!")
        print("✅ Assessment questions have Arabic translations")
        print("✅ Results page has Arabic translations")
        print("✅ Frontend can access all translations")
        print("✅ Ready for full Arabic localization testing")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Start frontend: cd frontend && npm run dev")
        print("2. Test language switching on homepage")
        print("3. Complete assessment in Arabic")
        print("4. Verify results page in Arabic")
        print("5. Test PDF generation in Arabic")
    else:
        print(f"\n🔧 ISSUES TO RESOLVE:")
        if not translations_added:
            print("- Fix database connection or translation insertion")
        if not questions_verified:
            print("- Add missing question translations")
        if not integration_working:
            print("- Start backend: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()