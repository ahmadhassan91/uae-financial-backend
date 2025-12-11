"""remove periods from arabic option labels

Revision ID: remove_arabic_periods
Revises: 75eceb034b5b
Create Date: 2025-12-11 12:38:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import json

# revision identifiers, used by Alembic.
revision = 'remove_arabic_periods'
down_revision = '75eceb034b5b'
branch_labels = None
depends_on = None


def upgrade():
    """Remove trailing periods from Arabic option labels."""
    
    # Get database connection
    connection = op.get_bind()
    
    # Fetch all question variations
    result = connection.execute(text("""
        SELECT id, options 
        FROM question_variations 
        WHERE options IS NOT NULL
    """))
    
    updated_count = 0
    
    for row in result:
        question_id = row[0]
        options_json = row[1]
        
        try:
            # Parse JSON options
            if isinstance(options_json, str):
                options = json.loads(options_json)
            else:
                options = options_json
            
            # Check if any Arabic labels have trailing periods
            has_periods = False
            for option in options:
                if 'label_ar' in option and option['label_ar']:
                    if option['label_ar'].rstrip().endswith(('.', '。', '،')):
                        has_periods = True
                        break
            
            if has_periods:
                # Remove trailing periods from all Arabic labels
                for option in options:
                    if 'label_ar' in option and option['label_ar']:
                        original = option['label_ar']
                        cleaned = original.rstrip('.。،').rstrip()
                        if cleaned != original:
                            option['label_ar'] = cleaned
                
                # Update the database
                connection.execute(
                    text("""
                        UPDATE question_variations 
                        SET options = :options 
                        WHERE id = :id
                    """),
                    {
                        'options': json.dumps(options, ensure_ascii=False),
                        'id': question_id
                    }
                )
                
                updated_count += 1
                
        except (json.JSONDecodeError, TypeError):
            continue
    
    print(f"Updated {updated_count} question variations")


def downgrade():
    """This migration cannot be reversed as we don't store the original periods."""
    pass
