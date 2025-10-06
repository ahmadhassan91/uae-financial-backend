#!/usr/bin/env python3

import asyncio
import asyncpg
import json
from app.localization.service import LocalizationService
from app.database import get_db

async def test_questions_api():
    """Test the questions API endpoint logic"""
    
    # Get database session
    async for db in get_db():
        service = LocalizationService(db)
        
        print("=== Testing Questions API ===")
        
        # Test getting Arabic questions
        try:
            questions = await service.get_questions_by_language('ar')
            print(f"\nFound {len(questions)} Arabic questions:")
            
            for q in questions[:3]:  # Show first 3
                print(f"  {q['id']}: {q['text'][:60]}...")
                if q.get('options'):
                    print(f"    Options: {len(q['options'])} available")
            
            if len(questions) > 3:
                print(f"  ... and {len(questions) - 3} more")
                
        except Exception as e:
            print(f"Error getting Arabic questions: {e}")
        
        # Test getting English questions
        try:
            questions = await service.get_questions_by_language('en')
            print(f"\nFound {len(questions)} English questions:")
            
            for q in questions[:3]:  # Show first 3
                print(f"  {q['id']}: {q['text'][:60]}...")
                if q.get('options'):
                    print(f"    Options: {len(q['options'])} available")
            
            if len(questions) > 3:
                print(f"  ... and {len(questions) - 3} more")
                
        except Exception as e:
            print(f"Error getting English questions: {e}")
        
        break  # Exit after first db session

if __name__ == "__main__":
    asyncio.run(test_questions_api())