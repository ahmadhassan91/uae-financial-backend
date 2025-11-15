#!/usr/bin/env python3
"""
Financial Clinic Data Migration: 16 Questions → 15 Questions

This script migrates existing Financial Clinic responses from the old 16-question
format to the new 15-question format by:
1. Removing fc_q16 (the old Q16 about education savings for children)
2. Recalculating scores with new weights (Q15 now 10% instead of 5%)
3. Recalculating status bands using new 4-band system
4. Regenerating insights with conditional logic
5. Updating total_questions field from 16 to 15

Usage:
    # Dry run (no changes made)
    python migrate_16_to_15_questions.py --dry-run
    
    # Actually perform migration
    python migrate_16_to_15_questions.py --execute
    
    # Rollback (restore from backup)
    python migrate_16_to_15_questions.py --rollback
"""
import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import FinancialClinicResponse, FinancialClinicProfile
from app.surveys.financial_clinic_scoring import calculate_financial_clinic_score
from app.surveys.financial_clinic_insights import generate_insights

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def backup_database(db: Session) -> str:
    """Create a backup of existing responses before migration."""
    backup_dir = Path(__file__).parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"financial_clinic_responses_{timestamp}.json"
    
    responses = db.query(FinancialClinicResponse).all()
    
    backup_data = {
        "timestamp": timestamp,
        "total_responses": len(responses),
        "responses": []
    }
    
    for response in responses:
        backup_data["responses"].append({
            "id": response.id,
            "profile_id": response.profile_id,
            "answers": response.answers,
            "total_score": response.total_score,
            "status_band": response.status_band,
            "category_scores": response.category_scores,
            "insights": response.insights,
            "product_recommendations": response.product_recommendations,
            "questions_answered": response.questions_answered,
            "total_questions": response.total_questions,
            "created_at": response.created_at.isoformat() if response.created_at else None
        })
    
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    return str(backup_file)


def migrate_response(response: FinancialClinicResponse, profile: FinancialClinicProfile, dry_run: bool = True) -> dict:
    """
    Migrate a single response from 16 to 15 questions.
    
    Returns dict with migration details.
    """
    result = {
        "id": response.id,
        "old_questions": response.total_questions,
        "old_score": response.total_score,
        "old_status_band": response.status_band,
        "success": False,
        "error": None
    }
    
    try:
        # 1. Remove fc_q16 from answers
        old_answers = response.answers.copy() if isinstance(response.answers, dict) else {}
        new_answers = {k: v for k, v in old_answers.items() if k != 'fc_q16'}
        
        if len(old_answers) == 16 and len(new_answers) != 15:
            result["error"] = f"Expected 15 questions after removing fc_q16, got {len(new_answers)}"
            return result
        
        # 2. Recalculate score with new system
        score_result = calculate_financial_clinic_score(responses=new_answers)
        
        # 3. Generate new insights with profile data
        profile_data = {
            'income_range': profile.income_range if profile else '',
            'nationality': profile.nationality if profile else '',
            'gender': profile.gender if profile else '',
            'children': profile.children if profile else 0
        }
        
        insights = generate_insights(
            category_scores=score_result["category_scores"],
            profile=profile_data,
            max_insights=5
        )
        
        # 4. Update response object (if not dry run)
        if not dry_run:
            response.answers = new_answers
            response.total_score = score_result["total_score"]
            response.status_band = score_result["status_band"]
            response.category_scores = score_result["category_scores"]
            response.insights = insights
            response.questions_answered = 15
            response.total_questions = 15
        
        result.update({
            "new_questions": 15,
            "new_score": score_result["total_score"],
            "new_status_band": score_result["status_band"],
            "score_change": score_result["total_score"] - response.total_score,
            "status_changed": score_result["status_band"] != response.status_band,
            "insights_count": len(insights),
            "success": True
        })
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def perform_migration(dry_run: bool = True):
    """Perform the migration of all responses."""
    print_header("Financial Clinic Migration: 16 → 15 Questions")
    
    if dry_run:
        print_warning("DRY RUN MODE - No changes will be made to database")
    else:
        print_info("EXECUTE MODE - Database will be updated")
    
    db = next(get_db())
    
    try:
        # Step 1: Create backup
        print_info("Step 1: Creating backup...")
        backup_file = backup_database(db)
        print_success(f"Backup created: {backup_file}")
        
        # Step 2: Get all responses
        print_info("\nStep 2: Loading responses from database...")
        responses = db.query(FinancialClinicResponse).all()
        print_success(f"Found {len(responses)} responses to migrate")
        
        # Step 3: Analyze responses
        print_info("\nStep 3: Analyzing responses...")
        responses_16q = [r for r in responses if r.total_questions == 16]
        responses_15q = [r for r in responses if r.total_questions == 15]
        responses_other = [r for r in responses if r.total_questions not in [15, 16]]
        
        print(f"  - Responses with 16 questions: {len(responses_16q)}")
        print(f"  - Responses with 15 questions: {len(responses_15q)}")
        print(f"  - Responses with other count: {len(responses_other)}")
        
        if len(responses_16q) == 0:
            print_success("\n✓ No migration needed - all responses already use 15 questions")
            return
        
        if len(responses_other) > 0:
            print_warning(f"\n⚠ Warning: {len(responses_other)} responses have unexpected question counts")
        
        # Step 4: Migrate each response
        print_info(f"\nStep 4: Migrating {len(responses_16q)} responses...")
        migration_results = []
        
        for i, response in enumerate(responses_16q, 1):
            # Get profile for conditional insights
            profile = db.query(FinancialClinicProfile).filter(
                FinancialClinicProfile.id == response.profile_id
            ).first()
            
            print(f"\n  [{i}/{len(responses_16q)}] Migrating response ID {response.id}...")
            result = migrate_response(response, profile, dry_run=dry_run)
            migration_results.append(result)
            
            if result["success"]:
                print(f"    Old: {result['old_questions']}Q, Score {result['old_score']:.1f}, {result['old_status_band']}")
                print(f"    New: {result['new_questions']}Q, Score {result['new_score']:.1f}, {result['new_status_band']}")
                print(f"    Change: {result['score_change']:+.1f} points, Status: {'CHANGED' if result['status_changed'] else 'Same'}")
                print(f"    Insights: {result['insights_count']} generated")
                print_success(f"    ✓ Migration successful")
            else:
                print_error(f"    ✗ Migration failed: {result['error']}")
        
        # Step 5: Commit changes (if not dry run)
        if not dry_run:
            print_info("\nStep 5: Committing changes to database...")
            db.commit()
            print_success("Changes committed successfully")
        else:
            print_info("\nStep 5: Rolling back (dry run mode)...")
            db.rollback()
            print_success("No changes made to database")
        
        # Step 6: Summary
        print_header("Migration Summary")
        
        successful = len([r for r in migration_results if r["success"]])
        failed = len([r for r in migration_results if not r["success"]])
        
        print(f"Total responses processed: {len(migration_results)}")
        print_success(f"Successful migrations: {successful}")
        if failed > 0:
            print_error(f"Failed migrations: {failed}")
        
        # Score changes
        score_changes = [r["score_change"] for r in migration_results if r["success"]]
        if score_changes:
            avg_change = sum(score_changes) / len(score_changes)
            print(f"\nAverage score change: {avg_change:+.1f} points")
            print(f"Min score change: {min(score_changes):+.1f} points")
            print(f"Max score change: {max(score_changes):+.1f} points")
        
        # Status band changes
        status_changes = len([r for r in migration_results if r.get("status_changed")])
        print(f"\nStatus band changes: {status_changes}/{successful}")
        
        # Backup location
        print(f"\nBackup saved to: {backup_file}")
        
        if dry_run:
            print_warning("\n⚠ DRY RUN COMPLETE - Run with --execute to apply changes")
        else:
            print_success("\n✓ MIGRATION COMPLETE")
        
    except Exception as e:
        print_error(f"\n✗ Migration failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration(backup_file: str):
    """Rollback migration from a backup file."""
    print_header("Rolling Back Migration")
    
    if not os.path.exists(backup_file):
        print_error(f"Backup file not found: {backup_file}")
        return
    
    db = next(get_db())
    
    try:
        # Load backup
        print_info("Loading backup file...")
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        print_success(f"Loaded backup with {backup_data['total_responses']} responses")
        print_info(f"Backup timestamp: {backup_data['timestamp']}")
        
        # Restore each response
        print_info("\nRestoring responses...")
        for i, backup_response in enumerate(backup_data['responses'], 1):
            response = db.query(FinancialClinicResponse).filter(
                FinancialClinicResponse.id == backup_response['id']
            ).first()
            
            if response:
                response.answers = backup_response['answers']
                response.total_score = backup_response['total_score']
                response.status_band = backup_response['status_band']
                response.category_scores = backup_response['category_scores']
                response.insights = backup_response['insights']
                response.product_recommendations = backup_response['product_recommendations']
                response.questions_answered = backup_response['questions_answered']
                response.total_questions = backup_response['total_questions']
                print_success(f"  [{i}/{len(backup_data['responses'])}] Restored response ID {response.id}")
        
        # Commit
        print_info("\nCommitting rollback...")
        db.commit()
        print_success("✓ Rollback complete")
        
    except Exception as e:
        print_error(f"✗ Rollback failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Financial Clinic responses from 16 to 15 questions"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without making changes (default)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually perform the migration'
    )
    parser.add_argument(
        '--rollback',
        type=str,
        metavar='BACKUP_FILE',
        help='Rollback migration from backup file'
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration(args.rollback)
    elif args.execute:
        perform_migration(dry_run=False)
    else:
        # Default to dry run
        perform_migration(dry_run=True)


if __name__ == "__main__":
    main()
