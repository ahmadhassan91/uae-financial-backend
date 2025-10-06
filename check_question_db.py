#!/usr/bin/env python3

import sqlite3
import os

# Connect to the database
db_path = 'financial_health.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for question translations
    cursor.execute("""
        SELECT content_id, language, text 
        FROM localized_content 
        WHERE content_type = 'question' 
        ORDER BY content_id, language
    """)
    
    results = cursor.fetchall()
    print(f'Found {len(results)} question translations in database:')
    
    current_id = None
    for content_id, language, text in results:
        if content_id != current_id:
            print(f'\n{content_id}:')
            current_id = content_id
        print(f'  {language}: {text[:80]}...')
    
    # Check what question IDs we have
    cursor.execute("""
        SELECT DISTINCT content_id 
        FROM localized_content 
        WHERE content_type = 'question' 
        ORDER BY content_id
    """)
    
    question_ids = [row[0] for row in cursor.fetchall()]
    print(f'\nQuestion IDs in database: {question_ids}')
    
    conn.close()
else:
    print('Database file not found')