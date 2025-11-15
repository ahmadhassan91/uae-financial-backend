"""
Populate Financial Clinic Products Database

This script populates the products table with National Bonds products
for the Financial Clinic recommendation system.

Products are organized by:
- 6 Categories (Income Stream, Savings Habit, etc.)
- 3 Status Levels (at_risk, good, excellent)
- Demographic filters (nationality, gender, children)

Run this script after database migration:
    python3 populate_financial_clinic_products.py
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Product


# Sample products based on Financial Clinic requirements
# Note: Client should provide complete product list
SAMPLE_PRODUCTS = [
    # ==================== INCOME STREAM ====================
    {
        "name": "myPlan starting with AED 100",
        "category": "Income Stream",
        "status_level": "at_risk",
        "description": "Start your savings journey with as little as AED 100 per month. Build financial stability gradually.",
        "nationality_filter": None,  # All nationalities
        "gender_filter": None,  # All genders
        "children_filter": None,  # All
        "priority": 1,
        "active": True
    },
    {
        "name": "Second Salary",
        "category": "Income Stream",
        "status_level": "good",
        "description": "Boost your income with our Second Salary plan. Create additional income streams for better financial security.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "My Million plan",
        "category": "Income Stream",
        "status_level": "excellent",
        "description": "Maximize your wealth-building potential with our Million plan for high-income earners.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    
    # ==================== SAVINGS HABIT ====================
    {
        "name": "Saving Bonds",
        "category": "Savings Habit",
        "status_level": "at_risk",
        "description": "Build a consistent savings habit with our flexible Saving Bonds. Start small and grow steadily.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "National Bonds Global Savings Club",
        "category": "Savings Habit",
        "status_level": "good",
        "description": "Join our Global Savings Club to optimize your savings with better returns and exclusive benefits.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "Booster offerings (3-5 years)",
        "category": "Savings Habit",
        "status_level": "excellent",
        "description": "Accelerate your wealth with our Booster products designed for disciplined savers.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    
    # ==================== EMERGENCY SAVINGS ====================
    {
        "name": "Ahed savings plan",
        "category": "Emergency Savings",
        "status_level": "good",
        "description": "Secure your family's future with Ahed savings plan, specifically designed for Emirati women.",
        "nationality_filter": "Emirati",
        "gender_filter": "Female",
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "myPlan emergency savings",
        "category": "Emergency Savings",
        "status_level": "good",
        "description": "Build a robust emergency fund with flexible contribution options.",
        "nationality_filter": "Non-Emirati",
        "gender_filter": None,
        "children_filter": None,
        "priority": 2,
        "active": True
    },
    {
        "name": "High-Yield Emergency Fund",
        "category": "Emergency Savings",
        "status_level": "excellent",
        "description": "Maximize returns on your emergency savings while maintaining liquidity.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    
    # ==================== DEBT MANAGEMENT ====================
    {
        "name": "Debt Consolidation Plan",
        "category": "Debt Management",
        "status_level": "at_risk",
        "description": "Simplify your finances by consolidating high-interest debts into manageable payments.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "Financial Wellness Program",
        "category": "Debt Management",
        "status_level": "good",
        "description": "Optimize your debt management with our comprehensive financial wellness program.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "Wealth Protection Plan",
        "category": "Debt Management",
        "status_level": "excellent",
        "description": "Maintain your excellent debt control while building wealth strategically.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    
    # ==================== RETIREMENT PLANNING ====================
    {
        "name": "Retirement Starter Plan",
        "category": "Retirement Planning",
        "status_level": "at_risk",
        "description": "Begin your retirement journey today with flexible contribution options.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "Golden Years Investment",
        "category": "Retirement Planning",
        "status_level": "good",
        "description": "Enhance your retirement savings with diversified investment options.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "Premium Retirement Portfolio",
        "category": "Retirement Planning",
        "status_level": "excellent",
        "description": "Optimize your retirement portfolio for maximum growth and security.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    
    # ==================== PROTECTING YOUR FAMILY ====================
    {
        "name": "Family Protection Essentials",
        "category": "Protecting Your Family",
        "status_level": "at_risk",
        "description": "Start protecting your family with essential Takaful coverage.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "Comprehensive Family Plan",
        "category": "Protecting Your Family",
        "status_level": "good",
        "description": "Comprehensive protection for your family's financial security.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": None,
        "priority": 1,
        "active": True
    },
    {
        "name": "My Million plan (Family)",
        "category": "Protecting Your Family",
        "status_level": "excellent",
        "description": "Premium wealth and protection plan for families with children.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": "1+",
        "priority": 1,
        "active": True
    },
    {
        "name": "Junior Million plan",
        "category": "Protecting Your Family",
        "status_level": "excellent",
        "description": "Secure your children's future with our dedicated education and protection plan.",
        "nationality_filter": None,
        "gender_filter": None,
        "children_filter": "1+",
        "priority": 2,
        "active": True
    },
]


def populate_products(db: Session):
    """Populate products table with sample data."""
    print("Starting product population...")
    
    # Check if products already exist
    existing_count = db.query(Product).count()
    if existing_count > 0:
        print(f"⚠️  Warning: {existing_count} products already exist in database.")
        response = input("Do you want to clear existing products and re-populate? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted. No changes made.")
            return
        
        # Clear existing products
        db.query(Product).delete()
        db.commit()
        print(f"✓ Cleared {existing_count} existing products")
    
    # Add new products
    added_count = 0
    for product_data in SAMPLE_PRODUCTS:
        product = Product(**product_data)
        db.add(product)
        added_count += 1
    
    db.commit()
    print(f"✓ Successfully added {added_count} products")
    
    # Display summary by category
    print("\n" + "="*60)
    print("PRODUCT SUMMARY BY CATEGORY")
    print("="*60)
    
    categories = db.query(Product.category).distinct().all()
    for (category,) in categories:
        count = db.query(Product).filter(Product.category == category).count()
        print(f"{category:30} {count} products")
    
    print("="*60)
    print(f"TOTAL: {added_count} products\n")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("FINANCIAL CLINIC PRODUCTS POPULATION")
    print("="*60 + "\n")
    
    db = SessionLocal()
    try:
        populate_products(db)
        print("\n✓ Product population completed successfully!\n")
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
