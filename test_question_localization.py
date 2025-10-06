#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.localization.service import LocalizationService
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

async def test_question_translations():
    # Get database session
    async for db in get_db():
        service = LocalizationService(db)
    
    print("=== Testing Question Localization ===")
    
    # Check what question translations exist in Arabic
    questions_ar = await service.get_content_by_type('question', 'ar')
    print(f'\nFound {len(questions_ar)} Arabic question translations:')
    for q in questions_ar:
        print(f'  {q.content_id}: {q.text[:80]}...')
    
    # Check what question translations exist in English
    questions_en = await service.get_content_by_type('question', 'en')
    print(f'\nFound {len(questions_en)} English question translations:')
    for q in questions_en[:5]:  # Show first 5
        print(f'  {q.content_id}: {q.text[:80]}...')
    
    if len(questions_en) > 5:
        print(f'  ... and {len(questions_en) - 5} more')
    
    # Check for specific question IDs that should exist
    expected_questions = [
        'q1_income_stability', 'q2_income_sources', 'q3_living_expenses',
        'q4_budget_tracking', 'q5_spending_control'
    ]
    
    print(f'\n=== Checking for expected question IDs ===')
    ar_question_ids = {q.content_id for q in questions_ar}
    en_question_ids = {q.content_id for q in questions_en}
    
    for qid in expected_questions:
        en_exists = qid in en_question_ids
        ar_exists = qid in ar_question_ids
        print(f'  {qid}: EN={en_exists}, AR={ar_exists}')
        
        if ar_exists:
            ar_q = next(q for q in questions_ar if q.content_id == qid)
            print(f'    AR: {ar_q.text}')
        break  # Exit after first db session

if __name__ == "__main__":
    asyncio.run(test_question_translations())