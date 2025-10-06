#!/usr/bin/env python3

import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_arabic_options():
    """Test if Arabic options are properly loaded"""
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/financial_health')
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check a specific question
        result = await conn.fetchrow("""
            SELECT content_id, text, options 
            FROM localized_content 
            WHERE content_type = 'question' 
            AND content_id = 'q4_budget_tracking' 
            AND language = 'ar'
        """)
        
        if result:
            print(f"Question: {result['content_id']}")
            print(f"Text: {result['text']}")
            print(f"Options: {json.dumps(result['options'], ensure_ascii=False, indent=2)}")
        else:
            print("Question not found")
        
        await conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(test_arabic_options())