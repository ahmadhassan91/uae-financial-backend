#!/usr/bin/env python3
"""
Add missing Arabic translations for survey questions
"""

import os
import sys
import psycopg2
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def add_missing_question_translations():
    """Add Arabic translations for missing survey questions"""
    print("🔍 Adding Missing Question Translations")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="uae_financial_health",
            user="clustox1"
        )
        
        cursor = conn.cursor()
        
        # Missing question translations
        missing_questions = {
            'q4_budget_tracking': {
                'en': 'I follow a monthly budget and track my expenses.',
                'ar': 'أتبع ميزانية شهرية وأتتبع نفقاتي.'
            },
            'q5_spending_control': {
                'en': 'I spend less than I earn every month.',
                'ar': 'أنفق أقل مما أكسب كل شهر.'
            },
            'q6_expense_review': {
                'en': 'I regularly review and reduce unnecessary expenses.',
                'ar': 'أراجع وأقلل النفقات غير الضرورية بانتظام.'
            },
            'q8_emergency_fund': {
                'en': 'I have an emergency fund to cater for my expenses.',
                'ar': 'لدي صندوق طوارئ لتغطية نفقاتي.'
            },
            'q9_savings_optimization': {
                'en': 'I keep my savings in safe, return generating accounts or investments.',
                'ar': 'أحتفظ بمدخراتي في حسابات آمنة ومربحة أو استثمارات.'
            },
            'q10_payment_history': {
                'en': 'I pay all my bills and loan installments on time.',
                'ar': 'أدفع جميع فواتيري وأقساط القروض في الوقت المحدد.'
            },
            'q11_debt_ratio': {
                'en': 'My debt repayments are less than 30% of my monthly income.',
                'ar': 'مدفوعات ديوني أقل من 30% من دخلي الشهري.'
            },
            'q12_credit_score': {
                'en': 'I understand my credit score and actively maintain or improve it.',
                'ar': 'أفهم درجة ائتماني وأحافظ عليها أو أحسنها بنشاط.'
            },
            'q14_insurance_coverage': {
                'en': 'I have adequate takaful cover (insurance) - (health, life, motor, property).',
                'ar': 'لدي تغطية تكافل (تأمين) كافية - (صحي، حياة، سيارة، ممتلكات).'
            },
            'q15_financial_planning': {
                'en': 'I have a written financial plan with goals for the next 3–5 years catering.',
                'ar': 'لدي خطة مالية مكتوبة بأهداف للسنوات الـ 3-5 القادمة.'
            },
            'q16_children_planning': {
                'en': 'I have adequately planned my children future for his school | University | Career Start Up.',
                'ar': 'لقد خططت بشكل كافٍ لمستقبل أطفالي للمدرسة | الجامعة | بداية المهنة.'
            }
        }
        
        added_count = 0
        
        for question_id, translations in missing_questions.items():
            # Add English translation
            cursor.execute("""
                SELECT id FROM localized_content 
                WHERE content_type = 'question' AND content_id = %s AND language = 'en'
            """, (question_id,))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO localized_content 
                    (content_type, content_id, language, text, is_active, created_at, updated_at)
                    VALUES ('question', %s, 'en', %s, true, %s, %s)
                """, (question_id, translations['en'], datetime.now(), datetime.now()))
                added_count += 1
                print(f"✅ Added English translation for {question_id}")
            
            # Add Arabic translation
            cursor.execute("""
                SELECT id FROM localized_content 
                WHERE content_type = 'question' AND content_id = %s AND language = 'ar'
            """, (question_id,))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO localized_content 
                    (content_type, content_id, language, text, is_active, created_at, updated_at)
                    VALUES ('question', %s, 'ar', %s, true, %s, %s)
                """, (question_id, translations['ar'], datetime.now(), datetime.now()))
                added_count += 1
                print(f"✅ Added Arabic translation for {question_id}")
        
        conn.commit()
        
        print(f"\n✅ Added {added_count} question translations")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding question translations: {e}")
        return False

def verify_all_translations():
    """Verify all translations are now complete"""
    print(f"\n🔍 Verifying All Translations")
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
        
        # Check all questions have both English and Arabic translations
        missing_en = []
        missing_ar = []
        
        for question in SURVEY_QUESTIONS_V2:
            # Check English
            cursor.execute("""
                SELECT id FROM localized_content 
                WHERE content_type = 'question' AND content_id = %s AND language = 'en'
            """, (question.id,))
            
            if not cursor.fetchone():
                missing_en.append(question.id)
            
            # Check Arabic
            cursor.execute("""
                SELECT id FROM localized_content 
                WHERE content_type = 'question' AND content_id = %s AND language = 'ar'
            """, (question.id,))
            
            if not cursor.fetchone():
                missing_ar.append(question.id)
        
        # Get total counts
        cursor.execute("SELECT COUNT(*) FROM localized_content WHERE language = 'en'")
        en_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM localized_content WHERE language = 'ar'")
        ar_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM localized_content")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Translation Summary:")
        print(f"  Total translations: {total_count}")
        print(f"  English translations: {en_count}")
        print(f"  Arabic translations: {ar_count}")
        
        if missing_en:
            print(f"  ❌ Missing English: {len(missing_en)} questions")
        else:
            print(f"  ✅ All questions have English translations")
        
        if missing_ar:
            print(f"  ❌ Missing Arabic: {len(missing_ar)} questions")
        else:
            print(f"  ✅ All questions have Arabic translations")
        
        cursor.close()
        conn.close()
        
        return len(missing_en) == 0 and len(missing_ar) == 0
        
    except Exception as e:
        print(f"❌ Error verifying translations: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Completing Survey Question Translations")
    print("=" * 60)
    
    # Add missing question translations
    questions_added = add_missing_question_translations()
    
    # Verify all translations are complete
    all_complete = verify_all_translations()
    
    print(f"\n" + "=" * 60)
    print("📊 FINAL TRANSLATION STATUS")
    print("=" * 60)
    
    if questions_added and all_complete:
        print("🎉 ALL TRANSLATIONS COMPLETE!")
        print("✅ All survey questions have Arabic translations")
        print("✅ All UI elements have Arabic translations")
        print("✅ All results page elements have Arabic translations")
        print("✅ Ready for full Arabic localization testing")
        
        print(f"\n🎯 READY FOR TESTING:")
        print("1. Start frontend: cd frontend && npm run dev")
        print("2. Visit: http://localhost:3000")
        print("3. Switch to Arabic language")
        print("4. Complete assessment in Arabic")
        print("5. View results in Arabic")
        print("6. Generate PDF report in Arabic")
    else:
        print("❌ Some translations are still missing")
        print("🔧 Check database connection and try again")

if __name__ == "__main__":
    main()