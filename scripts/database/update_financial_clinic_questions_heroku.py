"""
Update Financial Clinic Questions via Question Variations (Heroku Version)

This is a non-interactive version designed to run on Heroku.
It skips confirmation prompts and is safe to run via `heroku run`.

Usage:
    heroku run python3 scripts/database/update_financial_clinic_questions_heroku.py --app your-app-name
    heroku run python3 scripts/database/update_financial_clinic_questions_heroku.py --dry-run --app your-app-name
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import SessionLocal
from app.models import QuestionVariation
from app.surveys.financial_clinic_questions import (
    FINANCIAL_CLINIC_QUESTIONS,
    FinancialClinicQuestion,
    FinancialClinicOption
)


def convert_options_to_dict(options: List[FinancialClinicOption]) -> List[Dict[str, Any]]:
    """Convert FinancialClinicOption objects to dictionary format for database."""
    return [
        {
            "value": opt.value,
            "label_en": opt.label_en,
            "label_ar": opt.label_ar
        }
        for opt in options
    ]


def find_existing_variation(
    db: Session,
    base_question_id: str,
    variation_name: str = "default"
) -> Optional[QuestionVariation]:
    """Find existing question variation by base_question_id and variation_name."""
    return db.query(QuestionVariation).filter(
        and_(
            QuestionVariation.base_question_id == base_question_id,
            QuestionVariation.variation_name == variation_name
        )
    ).first()


def create_or_update_variation(
    db: Session,
    question: FinancialClinicQuestion,
    variation_name: str = "default",
    dry_run: bool = False
) -> Tuple[str, bool]:
    """
    Create or update a question variation.
    
    Returns:
        Tuple of (action_description, was_modified)
    """
    existing = find_existing_variation(db, question.id, variation_name)
    
    options_dict = convert_options_to_dict(question.options)
    
    if existing:
        # Check if update is needed
        needs_update = False
        changes = []
        
        if existing.text_en != question.text_en:
            needs_update = True
            changes.append("text_en")
        
        if existing.text_ar != question.text_ar:
            needs_update = True
            changes.append("text_ar")
        
        if existing.options != options_dict:
            needs_update = True
            changes.append("options")
        
        if existing.weight != question.weight:
            needs_update = True
            changes.append("weight")
        
        if existing.factor != question.category.value:
            needs_update = True
            changes.append("category")
        
        if needs_update:
            if not dry_run:
                existing.text_en = question.text_en
                existing.text_ar = question.text_ar
                existing.text = question.text_en  # For backward compatibility
                existing.options = options_dict
                existing.weight = question.weight
                existing.factor = question.category.value
                existing.updated_at = datetime.utcnow()
                db.commit()
            
            action = f"✓ UPDATED {question.id} (Q{question.number})"
            if changes:
                action += f" - Changed: {', '.join(changes)}"
            return action, True
        else:
            return f"  UNCHANGED {question.id} (Q{question.number})", False
    
    else:
        # Create new variation
        if not dry_run:
            new_variation = QuestionVariation(
                base_question_id=question.id,
                variation_name=variation_name,
                language="both",  # Bilingual
                text_en=question.text_en,
                text_ar=question.text_ar,
                text=question.text_en,  # For backward compatibility
                options=options_dict,
                demographic_rules=None,
                company_ids=None,
                factor=question.category.value,
                weight=question.weight,
                is_active=True
            )
            db.add(new_variation)
            db.commit()
        
        return f"✓ CREATED {question.id} (Q{question.number})", True


def update_all_questions(
    variation_name: str = "default",
    dry_run: bool = False
) -> None:
    """
    Update all Financial Clinic questions.
    
    Args:
        variation_name: Name of the variation to update (default: "default")
        dry_run: If True, show what would be updated without making changes
    """
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("Financial Clinic Question Update Script (Heroku)")
        print("=" * 80)
        print(f"Variation Name: {variation_name}")
        print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE UPDATE'}")
        print(f"Total Questions: {len(FINANCIAL_CLINIC_QUESTIONS)}")
        print(f"Database: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
        print("=" * 80)
        print()
        
        updated_count = 0
        created_count = 0
        unchanged_count = 0
        
        for question in FINANCIAL_CLINIC_QUESTIONS:
            action, was_modified = create_or_update_variation(
                db, question, variation_name, dry_run
            )
            print(action)
            
            if was_modified:
                if "CREATED" in action:
                    created_count += 1
                else:
                    updated_count += 1
            else:
                unchanged_count += 1
        
        print()
        print("=" * 80)
        print("Summary:")
        print(f"  Created: {created_count}")
        print(f"  Updated: {updated_count}")
        print(f"  Unchanged: {unchanged_count}")
        print(f"  Total: {len(FINANCIAL_CLINIC_QUESTIONS)}")
        print("=" * 80)
        
        if dry_run:
            print()
            print("⚠️  DRY RUN MODE - No changes were made to the database")
            print("   Run without --dry-run to apply these changes")
        else:
            print()
            print("✓ All changes have been applied successfully!")
            print("✓ Questions are now live in production!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update Financial Clinic questions on Heroku (non-interactive)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--variation-name",
        type=str,
        default="default",
        help="Name of the variation to update (default: 'default')"
    )
    
    args = parser.parse_args()
    
    # No confirmation needed - this is designed for Heroku
    if not args.dry_run:
        print("⚠️  LIVE UPDATE MODE - Changes will be applied to production database")
        print()
    
    update_all_questions(
        variation_name=args.variation_name,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
