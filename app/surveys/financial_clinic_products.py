"""
Financial Clinic Product Recommendation Engine

Matches users with appropriate National Bonds products based on:
- Category scores (which areas need improvement)
- Status levels (at_risk, good, excellent)
- Demographics (nationality, gender, children)
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models import Product


class ProductRecommendationEngine:
    """Match users with appropriate products."""
    
    MAX_RECOMMENDATIONS = 3  # Maximum products to recommend
    
    def __init__(self, db: Session):
        """
        Initialize recommendation engine.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_recommendations(
        self,
        category_scores: Dict[str, Dict],
        nationality: str,
        gender: Optional[str] = None,
        children: int = 0
    ) -> List[Product]:
        """
        Get product recommendations for a user.
        
        Args:
            category_scores: Category scores from scoring engine
                Example:
                {
                    "Income Stream": {"score": 12.0, "status_level": "good"},
                    "Savings Habit": {"score": 8.5, "status_level": "at_risk"},
                    ...
                }
            nationality: User nationality ("Emirati" or "Non-Emirati")
            gender: User gender ("Male" or "Female")
            children: Number of children (0-5+)
            
        Returns:
            List of up to 3 Product objects, prioritized
        """
        # Rank categories by score (lowest first = highest priority)
        ranked_categories = self._rank_categories(category_scores)
        
        recommended_products = []
        seen_products = set()  # Track to avoid duplicates
        
        # Iterate through categories from lowest to highest score
        for category_name, score_data in ranked_categories:
            if len(recommended_products) >= self.MAX_RECOMMENDATIONS:
                break
            
            status_level = score_data["status_level"]
            
            # Find matching products
            products = self._find_products(
                category=category_name,
                status_level=status_level,
                nationality=nationality,
                gender=gender,
                children=children
            )
            
            # Add products (up to max limit)
            for product in products:
                if product.id not in seen_products:
                    recommended_products.append(product)
                    seen_products.add(product.id)
                    
                    if len(recommended_products) >= self.MAX_RECOMMENDATIONS:
                        break
        
        return recommended_products
    
    def _rank_categories(
        self,
        category_scores: Dict[str, Dict]
    ) -> List[tuple]:
        """
        Rank categories by score (lowest first).
        
        Args:
            category_scores: Category scores dictionary
            
        Returns:
            List of (category_name, score_data) tuples
        """
        # Sort by score (ascending)
        return sorted(
            category_scores.items(),
            key=lambda x: x[1].get("score", 0)
        )
    
    def _find_products(
        self,
        category: str,
        status_level: str,
        nationality: str,
        gender: Optional[str] = None,
        children: int = 0
    ) -> List[Product]:
        """
        Find products matching criteria.
        
        Args:
            category: Category name
            status_level: "at_risk", "good", or "excellent"
            nationality: User nationality
            gender: User gender
            children: Number of children
            
        Returns:
            List of matching Product objects
        """
        # Query products for this category and status level
        query = self.db.query(Product).filter(
            Product.category == category,
            Product.status_level == status_level,
            Product.active == True
        )
        
        products = query.all()
        
        # Filter by demographics
        matching_products = [
            p for p in products
            if p.matches_demographics(nationality, gender, children)
        ]
        
        # Sort by priority
        matching_products.sort(key=lambda p: p.priority)
        
        return matching_products


def get_product_recommendations(
    db: Session,
    category_scores: Dict[str, Dict],
    nationality: str,
    gender: Optional[str] = None,
    children: int = 0
) -> List[Dict]:
    """
    Convenience function to get product recommendations.
    
    Args:
        db: Database session
        category_scores: Category scores from scoring engine
        nationality: User nationality
        gender: User gender
        children: Number of children
        
    Returns:
        List of product dictionaries
    """
    engine = ProductRecommendationEngine(db)
    products = engine.get_recommendations(
        category_scores=category_scores,
        nationality=nationality,
        gender=gender,
        children=children
    )
    
    return [
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "description": product.description,
            "priority": product.priority
        }
        for product in products
    ]
