#!/usr/bin/env python3
"""
Data Migration Script: Update Financial Clinic from 16 to 15 Questions

This script migrates existing Financial Clinic responses from the old 16-question 
format to the new 15-question format by:
1. Removing Q16 (fc_q16) from all response answers
2. Updating total_questions from 16 to 15
3. Updating questions_answered accordingly
4. Recalculating scores based on new weights
5. Regenerating insights with conditional logic

Usage:
    python migrate_financial_clinic_15_questions.py [--dry-run]
    
Options:
    --dry-run    Show what would be changed without making actual changes
"""
import sys
import argparse
import json
from datetime import datetime

sys.path.insert(0, '/Users/clustox_1/Documents/uae-financial-health/backend')

from app.database import SessionLocal
from app.models import FinancialClinicResponse, FinancialClinicProfile
from app.surveys.financial_clinic_scoring import calculate_financial_clinic_score
from app.surveys.financial_clinic_insights import generate_insights


def migrate_response(response, profile, dry_run=False):
    """
    Migrate a single Financial Clinic response from 16 to 15 questions.
    
    Args:
        response: FinancialClinicResponse object
        profile: FinancialClinicProfile object
        dry_run: If True, don't save changes
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Parse answers
        answers = response.answers if isinstance(response.answers, dict) else json.loads(response.answers)
        
        # Check if Q16 exists
        if 'fc_q16' not in answers:
            return False, f"Response {response.id}: Already migrated (no Q16 found)"
        
        # Remove Q16
        old_answer_count = len(answers)
        del answers['fc_q16']
        new_answer_count = len(answers)
        
        # Recalculate score with new 15-question system
        score_result = calculate_financial_clinic_score(responses=answers)
        
        # Generate new insights with profile data
        insights = generate_insights(
            category_scores=score_result["category_scores"],
            profile={
                'income_range': profile.income_range,
                'nationality': profile.nationality,
                'gender': profile.gender,
                'children': profile.children
            },
            max_insights=5
        )
        
        if dry_run:
            return True, f"""Response {response.id}: Would migrate
  - Questions: {old_answer_count} → {new_answer_count}
  - Old Score: {response.total_score} → New Score: {score_result['total_score']}
  - Old Band: {response.status_band} → New Band: {score_result['status_band']}
  - Insights: {len(response.insights or [])} → {len(insights)}"""
        
        # Update response
        response.answers = answers
        response.total_questions = 15
        response.questions_answered = new_answer_count
        response.total_score = score_result['total_score']
        response.status_band = score_result['status_band']
        response.category_scores = score_result['category_scores']
        response.insights = insights
        
        return True, f"""Response {response.id}: Migrated successfully
  - Questions: {old_answer_count} → {new_answer_count}
  - Score: {response.total_score:.1f} ({response.status_band})
  - Insights: {len(insights)}"""
        
    except Exception as e:
        return False, f"Response {response.id}: Error - {str(e)}"


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='Migrate Financial Clinic from 16 to 15 questions')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    print("=" * 80)
    print("FINANCIAL CLINIC DATA MIGRATION: 16 → 15 QUESTIONS")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE MIGRATION'}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    db = SessionLocal()
    
    try:
        # Get all Financial Clinic responses
        responses = db.query(FinancialClinicResponse).all()
        total = len(responses)
        
        print(f"Found {total} Financial Clinic responses to migrate")
        print()
        
        if total == 0:
            print("✅ No responses to migrate. Database is ready!")
            return 0
        
        # Migrate each response
        success_count = 0
        already_migrated = 0
        error_count = 0
        
        for i, response in enumerate(responses, 1):
            # Get profile
            profile = db.query(FinancialClinicProfile).filter(
                FinancialClinicProfile.id == response.profile_id
            ).first()
            
            if not profile:
                print(f"❌ Response {response.id}: No profile found (profile_id: {response.profile_id})")
                error_count += 1
                continue
            
            # Migrate
            success, message = migrate_response(response, profile, args.dry_run)
            
            if success:
                if "Already migrated" in message:
                    print(f"⏭️  {message}")
                    already_migrated += 1
                else:
                    print(f"✅ {message}")
                    success_count += 1
            else:
                print(f"❌ {message}")
                error_count += 1
        
        print()
        print("=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        print(f"Total Responses:      {total}")
        print(f"Successfully Migrated: {success_count}")
        print(f"Already Migrated:     {already_migrated}")
        print(f"Errors:               {error_count}")
        print()
        
        if args.dry_run:
            print("⚠️  DRY RUN MODE - No changes were saved to the database")
            print("   Run without --dry-run to apply changes")
        else:
            if success_count > 0:
                # Commit changes
                db.commit()
                print("✅ All changes committed to database")
            else:
                print("ℹ️  No changes to commit")
        
        print()
        return 0 if error_count == 0 else 1
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ MIGRATION FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        db.rollback()
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
