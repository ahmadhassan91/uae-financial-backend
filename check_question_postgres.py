#!/usr/bin/env python3

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_question_translations():
    # Connect to PostgreSQL
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/financial_health')
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check for question translations
        results = await conn.fetch("""
            SELECT content_id, language, text 
            FROM localized_content 
            WHERE content_type = 'question' 
            ORDER BY content_id, language
        """)
        
        print(f'Found {len(results)} question translations in database:')
        
        current_id = None
        for row in results:
            content_id, language, text = row['content_id'], row['language'], row['text']
            if content_id != current_id:
                print(f'\n{content_id}:')
                current_id = content_id
            print(f'  {language}: {text[:80]}...')
        
        # Check what question IDs we have
        question_ids = await conn.fetch("""
            SELECT DISTINCT content_id 
            FROM localized_content 
            WHERE content_type = 'question' 
            ORDER BY content_id
        """)
        
        ids = [row['content_id'] for row in question_ids]
        print(f'\nQuestion IDs in database: {ids}')
        
        # Check for specific frontend question IDs
        frontend_questions = [
            'q1_income_stability', 'q2_income_sources', 'q3_living_expenses',
            'q4_budget_tracking', 'q5_spending_control', 'q6_expense_review'
        ]
        
        print(f'\nChecking for frontend question IDs:')
        for qid in frontend_questions:
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM localized_content 
                WHERE content_type = 'question' AND content_id = $1
            """, qid)
            print(f'  {qid}: {count} translations found')
        
        await conn.close()
        
    except Exception as e:
        print(f'Error connecting to database: {e}')

if __name__ == "__main__":
    asyncio.run(check_question_translations())