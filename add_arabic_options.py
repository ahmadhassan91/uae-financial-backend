#!/usr/bin/env python3

import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def add_arabic_options():
    """Add missing Arabic option translations to the database"""
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/financial_health')
    
    # Arabic option translations for questions that are missing them
    arabic_options = {
        'q4_budget_tracking': [
            {"value": 5, "label": "باستمرار كل شهر"},
            {"value": 4, "label": "بشكل متكرر ولكن ليس باستمرار"},
            {"value": 3, "label": "أحياناً"},
            {"value": 2, "label": "بشكل عشوائي"},
            {"value": 1, "label": "لا أتتبع"}
        ],
        'q5_spending_control': [
            {"value": 5, "label": "باستمرار كل شهر"},
            {"value": 4, "label": "بشكل متكرر ولكن ليس باستمرار"},
            {"value": 3, "label": "أحياناً"},
            {"value": 2, "label": "بشكل عشوائي"},
            {"value": 1, "label": "أكثر من أو كل أرباحي"}
        ],
        'q6_expense_review': [
            {"value": 5, "label": "باستمرار كل شهر"},
            {"value": 4, "label": "بشكل متكرر ولكن ليس باستمرار"},
            {"value": 3, "label": "أحياناً"},
            {"value": 2, "label": "بشكل عشوائي"},
            {"value": 1, "label": "لا أتتبع"}
        ],
        'q7_savings_rate': [
            {"value": 5, "label": "20% أو أكثر"},
            {"value": 4, "label": "أقل من 20%"},
            {"value": 3, "label": "أقل من 10%"},
            {"value": 2, "label": "5% أو أقل"},
            {"value": 1, "label": "0%"}
        ],
        'q8_emergency_fund': [
            {"value": 5, "label": "6+ أشهر"},
            {"value": 4, "label": "3 - 6 أشهر"},
            {"value": 3, "label": "شهرين"},
            {"value": 2, "label": "شهر واحد"},
            {"value": 1, "label": "لا يوجد"}
        ],
        'q9_savings_optimization': [
            {"value": 5, "label": "آمن | أسعى لتحسين العائد باستمرار"},
            {"value": 4, "label": "آمن | أسعى لتحسين العائد معظم الأوقات"},
            {"value": 3, "label": "حساب توفير بعوائد قليلة"},
            {"value": 2, "label": "حساب جاري"},
            {"value": 1, "label": "نقد"}
        ],
        'q10_payment_history': [
            {"value": 5, "label": "باستمرار كل شهر"},
            {"value": 4, "label": "بشكل متكرر ولكن ليس باستمرار"},
            {"value": 3, "label": "أحياناً"},
            {"value": 2, "label": "بشكل عشوائي"},
            {"value": 1, "label": "فوت المدفوعات معظم الأوقات"}
        ],
        'q11_debt_ratio': [
            {"value": 5, "label": "لا يوجد دين"},
            {"value": 4, "label": "20% أو أقل من الدخل الشهري"},
            {"value": 3, "label": "أقل من 30% من الدخل الشهري"},
            {"value": 2, "label": "30% أو أكثر من الدخل الشهري"},
            {"value": 1, "label": "50% أو أكثر من الدخل الشهري"}
        ],
        'q12_credit_score': [
            {"value": 5, "label": "100% وأراقبها باستمرار"},
            {"value": 4, "label": "100% وأراقبها بشكل متكرر"},
            {"value": 3, "label": "أفهم إلى حد ما ومراقبة متكررة"},
            {"value": 2, "label": "أفهم إلى حد ما وأحافظ عليها بشكل عشوائي"},
            {"value": 1, "label": "لا أفهم ولا أحافظ عليها"}
        ],
        'q14_insurance_coverage': [
            {"value": 5, "label": "100% تغطية كافية للحماية المطلوبة"},
            {"value": 4, "label": "80% تغطية للحماية المطلوبة"},
            {"value": 3, "label": "50% تغطية للحماية المطلوبة"},
            {"value": 2, "label": "25% تغطية للحماية المطلوبة"},
            {"value": 1, "label": "لا توجد تغطية"}
        ],
        'q15_financial_planning': [
            {"value": 5, "label": "خطة مالية مختصرة ومراجعة باستمرار"},
            {"value": 4, "label": "خطة مالية واسعة ومراجعة بشكل متكرر"},
            {"value": 3, "label": "أهداف عالية المستوى ومراجعة أحياناً"},
            {"value": 2, "label": "خطة عشوائية | مراجعات"},
            {"value": 1, "label": "لا توجد خطة مالية"}
        ],
        'q16_children_planning': [
            {"value": 5, "label": "100% مدخرات كافية للجوانب الثلاثة"},
            {"value": 4, "label": "80% مدخرات للجوانب الثلاثة"},
            {"value": 3, "label": "50% مدخرات للجوانب الثلاثة"},
            {"value": 2, "label": "خطة عشوائية للجوانب الثلاثة"},
            {"value": 1, "label": "لا توجد خطة"}
        ]
    }
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        updated_count = 0
        
        for question_id, options in arabic_options.items():
            # Update the Arabic question with the new options
            result = await conn.execute("""
                UPDATE localized_content 
                SET options = $1
                WHERE content_type = 'question' 
                AND content_id = $2 
                AND language = 'ar'
            """, json.dumps(options), question_id)
            
            if result == "UPDATE 1":
                updated_count += 1
                print(f"Updated options for {question_id}")
            else:
                print(f"No update for {question_id} (not found or no change)")
        
        print(f"\nUpdated {updated_count} questions with Arabic options")
        
        await conn.close()
        
    except Exception as e:
        print(f'Error updating Arabic options: {e}')

if __name__ == "__main__":
    asyncio.run(add_arabic_options())