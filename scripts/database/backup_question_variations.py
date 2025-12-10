"""
Backup Question Variations

This script creates a backup of all question variations before updating them.
The backup is saved as a JSON file with timestamp.

Usage:
    python scripts/database/backup_question_variations.py [--output-dir backups]
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse
import json
from datetime import datetime
from typing import List, Dict, Any

from app.database import SessionLocal
from app.models import QuestionVariation


def serialize_variation(variation: QuestionVariation) -> Dict[str, Any]:
    """Convert QuestionVariation object to JSON-serializable dictionary."""
    return {
        "id": variation.id,
        "base_question_id": variation.base_question_id,
        "variation_name": variation.variation_name,
        "language": variation.language,
        "text_en": variation.text_en,
        "text_ar": variation.text_ar,
        "text": variation.text,
        "options": variation.options,
        "demographic_rules": variation.demographic_rules,
        "company_ids": variation.company_ids,
        "factor": variation.factor,
        "weight": variation.weight,
        "is_active": variation.is_active,
        "created_at": variation.created_at.isoformat() if variation.created_at else None,
        "updated_at": variation.updated_at.isoformat() if variation.updated_at else None,
    }


def backup_variations(output_dir: str = "backups") -> str:
    """
    Backup all question variations to a JSON file.
    
    Args:
        output_dir: Directory to save backup file
        
    Returns:
        Path to the backup file
    """
    db = SessionLocal()
    
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get all variations
        variations = db.query(QuestionVariation).all()
        
        # Serialize variations
        backup_data = {
            "backup_timestamp": datetime.utcnow().isoformat(),
            "total_variations": len(variations),
            "variations": [serialize_variation(v) for v in variations]
        }
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"question_variations_backup_{timestamp}.json"
        filepath = output_path / filename
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print("=" * 80)
        print("Question Variations Backup")
        print("=" * 80)
        print(f"Total Variations: {len(variations)}")
        print(f"Backup File: {filepath}")
        print(f"File Size: {filepath.stat().st_size:,} bytes")
        print("=" * 80)
        
        # Show summary by base question
        by_question = {}
        for v in variations:
            if v.base_question_id not in by_question:
                by_question[v.base_question_id] = []
            by_question[v.base_question_id].append(v.variation_name)
        
        print("\nVariations by Question:")
        for qid in sorted(by_question.keys()):
            print(f"  {qid}: {len(by_question[qid])} variation(s) - {', '.join(by_question[qid])}")
        
        print("\n✓ Backup completed successfully!")
        
        return str(filepath)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


def restore_from_backup(backup_file: str, dry_run: bool = False) -> None:
    """
    Restore question variations from a backup file.
    
    Args:
        backup_file: Path to backup JSON file
        dry_run: If True, show what would be restored without making changes
    """
    db = SessionLocal()
    
    try:
        # Load backup file
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print("=" * 80)
        print("Restore Question Variations from Backup")
        print("=" * 80)
        print(f"Backup File: {backup_file}")
        print(f"Backup Timestamp: {backup_data['backup_timestamp']}")
        print(f"Total Variations: {backup_data['total_variations']}")
        print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE RESTORE'}")
        print("=" * 80)
        print()
        
        if not dry_run:
            response = input("⚠️  This will overwrite existing variations. Continue? (yes/no): ")
            if response.lower() not in ["yes", "y"]:
                print("Restore cancelled.")
                return
            print()
        
        restored_count = 0
        skipped_count = 0
        
        for var_data in backup_data['variations']:
            # Check if variation exists
            existing = db.query(QuestionVariation).filter(
                QuestionVariation.id == var_data['id']
            ).first()
            
            if existing:
                if not dry_run:
                    # Update existing
                    for key, value in var_data.items():
                        if key not in ['id', 'created_at', 'updated_at']:
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                
                print(f"✓ Updated: {var_data['base_question_id']} - {var_data['variation_name']}")
                restored_count += 1
            else:
                if not dry_run:
                    # Create new
                    new_var = QuestionVariation(**{
                        k: v for k, v in var_data.items()
                        if k not in ['id', 'created_at', 'updated_at']
                    })
                    db.add(new_var)
                
                print(f"✓ Created: {var_data['base_question_id']} - {var_data['variation_name']}")
                restored_count += 1
        
        if not dry_run:
            db.commit()
        
        print()
        print("=" * 80)
        print("Summary:")
        print(f"  Restored: {restored_count}")
        print(f"  Skipped: {skipped_count}")
        print("=" * 80)
        
        if dry_run:
            print("\n⚠️  DRY RUN MODE - No changes were made")
        else:
            print("\n✓ Restore completed successfully!")
        
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
        description="Backup and restore question variations"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="backups",
        help="Directory to save backup file (default: backups)"
    )
    parser.add_argument(
        "--restore",
        type=str,
        metavar="BACKUP_FILE",
        help="Restore from backup file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be restored without making changes (only for restore)"
    )
    
    args = parser.parse_args()
    
    if args.restore:
        restore_from_backup(args.restore, args.dry_run)
    else:
        backup_variations(args.output_dir)


if __name__ == "__main__":
    main()
