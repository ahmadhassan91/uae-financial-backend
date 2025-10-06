"""
Admin API routes for demographic rule management.

This module provides REST API endpoints for creating, managing, and analyzing
demographic rules with proper validation and testing capabilities.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.database import get_db
from app.auth.dependencies import get_current_admin_user as get_admin_user
from app.models import (
    User, DemographicRule, CustomerProfile, SurveyResponse, AuditLog
)
from app.surveys.demographic_rule_engine import DemographicRuleEngine
from app.admin.schemas import (
    DemographicRuleCreate, DemographicRuleUpdate, DemographicRuleResponse,
    DemographicRuleAnalytics, RuleTestRequest, RuleTestResult,
    DemographicRuleListResponse, RuleValidationResult
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/demographic-rules", tags=["admin", "demographic-rules"])


@router.get("/", response_model=DemographicRuleListResponse)
async def list_demographic_rules(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
    active_only: bool = Query(True, description="Only return active rules"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    """
    List demographic rules with filtering and pagination.
    """
    try:
        # Build query
        query = db.query(DemographicRule)
        
        if active_only:
            query = query.filter(DemographicRule.is_active == True)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        rules = query.order_by(DemographicRule.priority.asc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        rule_responses = []
        for rule in rules:
            # Get usage statistics
            usage_count = db.query(SurveyResponse).filter(
                SurveyResponse.demographic_rules_applied.contains([rule.id])
            ).count()
            
            rule_response = DemographicRuleResponse(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                conditions=rule.conditions,
                actions=rule.actions,
                priority=rule.priority,
                is_active=rule.is_active,
                usage_count=usage_count,
                created_at=rule.created_at,
                updated_at=rule.updated_at
            )
            rule_responses.append(rule_response)
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="list_demographic_rules",
            entity_type="demographic_rule",
            details={
                "filters": {"active_only": active_only},
                "total_results": total
            }
        ))
        db.commit()
        
        return DemographicRuleListResponse(
            rules=rule_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=(total + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Error listing demographic rules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving demographic rules"
        )


@router.post("/", response_model=DemographicRuleResponse)
async def create_demographic_rule(
    rule_data: DemographicRuleCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Create a new demographic rule.
    """
    try:
        # Validate rule
        rule_engine = DemographicRuleEngine(db)
        validation = rule_engine.validate_rule({
            'conditions': rule_data.conditions,
            'actions': rule_data.actions
        })
        
        if not validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rule validation failed: {'; '.join(validation['errors'])}"
            )
        
        # Check for duplicate names
        existing = db.query(DemographicRule).filter(
            DemographicRule.name == rule_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A rule with this name already exists"
            )
        
        # Create rule
        rule = DemographicRule(
            name=rule_data.name,
            description=rule_data.description,
            conditions=rule_data.conditions,
            actions=rule_data.actions,
            priority=rule_data.priority,
            is_active=rule_data.is_active
        )
        
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="create_demographic_rule",
            entity_type="demographic_rule",
            entity_id=rule.id,
            details={
                "rule_name": rule.name,
                "priority": rule.priority
            }
        ))
        db.commit()
        
        return DemographicRuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            conditions=rule.conditions,
            actions=rule.actions,
            priority=rule.priority,
            is_active=rule.is_active,
            usage_count=0,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating demographic rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating demographic rule"
        )


@router.get("/{rule_id}", response_model=DemographicRuleResponse)
async def get_demographic_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Get a specific demographic rule by ID.
    """
    try:
        rule = db.query(DemographicRule).filter(
            DemographicRule.id == rule_id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demographic rule not found"
            )
        
        # Get usage statistics
        usage_count = db.query(SurveyResponse).filter(
            SurveyResponse.demographic_rules_applied.contains([rule.id])
        ).count()
        
        return DemographicRuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            conditions=rule.conditions,
            actions=rule.actions,
            priority=rule.priority,
            is_active=rule.is_active,
            usage_count=usage_count,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting demographic rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving demographic rule"
        )


@router.put("/{rule_id}", response_model=DemographicRuleResponse)
async def update_demographic_rule(
    rule_id: int,
    rule_data: DemographicRuleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Update a demographic rule.
    """
    try:
        rule = db.query(DemographicRule).filter(
            DemographicRule.id == rule_id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demographic rule not found"
            )
        
        # Validate updates if conditions or actions changed
        if rule_data.conditions or rule_data.actions:
            rule_engine = DemographicRuleEngine(db)
            validation = rule_engine.validate_rule({
                'conditions': rule_data.conditions or rule.conditions,
                'actions': rule_data.actions or rule.actions
            })
            
            if not validation['valid']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rule validation failed: {'; '.join(validation['errors'])}"
                )
        
        # Update fields
        if rule_data.name is not None:
            # Check for duplicate names
            existing = db.query(DemographicRule).filter(
                and_(
                    DemographicRule.name == rule_data.name,
                    DemographicRule.id != rule_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A rule with this name already exists"
                )
            
            rule.name = rule_data.name
        
        if rule_data.description is not None:
            rule.description = rule_data.description
        if rule_data.conditions is not None:
            rule.conditions = rule_data.conditions
        if rule_data.actions is not None:
            rule.actions = rule_data.actions
        if rule_data.priority is not None:
            rule.priority = rule_data.priority
        if rule_data.is_active is not None:
            rule.is_active = rule_data.is_active
        
        rule.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(rule)
        
        # Get usage statistics
        usage_count = db.query(SurveyResponse).filter(
            SurveyResponse.demographic_rules_applied.contains([rule.id])
        ).count()
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="update_demographic_rule",
            entity_type="demographic_rule",
            entity_id=rule.id,
            details={
                "updated_fields": [k for k, v in rule_data.dict().items() if v is not None]
            }
        ))
        db.commit()
        
        return DemographicRuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            conditions=rule.conditions,
            actions=rule.actions,
            priority=rule.priority,
            is_active=rule.is_active,
            usage_count=usage_count,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating demographic rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating demographic rule"
        )


@router.delete("/{rule_id}")
async def delete_demographic_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Delete a demographic rule.
    """
    try:
        rule = db.query(DemographicRule).filter(
            DemographicRule.id == rule_id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demographic rule not found"
            )
        
        # Check if rule is being used in any surveys
        usage_count = db.query(SurveyResponse).filter(
            SurveyResponse.demographic_rules_applied.contains([rule.id])
        ).count()
        
        if usage_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete rule that has been used in {usage_count} surveys. Deactivate instead."
            )
        
        db.delete(rule)
        db.commit()
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="delete_demographic_rule",
            entity_type="demographic_rule",
            entity_id=rule_id,
            details={"rule_name": rule.name}
        ))
        db.commit()
        
        return {"message": "Demographic rule deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting demographic rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting demographic rule"
        )


@router.post("/test", response_model=RuleTestResult)
async def test_demographic_rule(
    test_request: RuleTestRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Test a demographic rule against sample profiles.
    """
    try:
        rule_engine = DemographicRuleEngine(db)
        
        # Validate rule
        validation = rule_engine.validate_rule({
            'conditions': test_request.conditions,
            'actions': test_request.actions
        })
        
        # Test against sample profiles if provided
        profile_matches = []
        if test_request.test_profiles:
            for profile_data in test_request.test_profiles:
                try:
                    # Create temporary profile object for testing
                    profile = CustomerProfile(**profile_data)
                    
                    # Convert profile to context
                    context = rule_engine._profile_to_context(profile)
                    
                    # Evaluate conditions
                    matches = rule_engine._evaluate_conditions(test_request.conditions, context)
                    
                    profile_matches.append({
                        "profile": profile_data,
                        "matches": matches,
                        "context": context
                    })
                    
                except Exception as e:
                    profile_matches.append({
                        "profile": profile_data,
                        "matches": False,
                        "error": str(e)
                    })
        
        # Calculate estimated impact
        total_profiles = len(test_request.test_profiles) if test_request.test_profiles else 0
        matching_profiles = len([m for m in profile_matches if m.get("matches", False)])
        
        estimated_impact = {
            "total_tested": total_profiles,
            "matching_profiles": matching_profiles,
            "match_rate": matching_profiles / total_profiles if total_profiles > 0 else 0.0,
            "affected_questions": len(test_request.actions.get("include_questions", [])) + 
                                len(test_request.actions.get("exclude_questions", [])) + 
                                len(test_request.actions.get("add_questions", []))
        }
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="test_demographic_rule",
            entity_type="demographic_rule",
            details={
                "validation_result": validation['valid'],
                "profiles_tested": total_profiles,
                "matching_profiles": matching_profiles
            }
        ))
        db.commit()
        
        return RuleTestResult(
            validation=RuleValidationResult(
                valid=validation['valid'],
                errors=validation['errors'],
                warnings=validation['warnings']
            ),
            profile_matches=profile_matches,
            estimated_impact=estimated_impact
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing demographic rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error testing demographic rule"
        )


@router.get("/analytics/overview", response_model=DemographicRuleAnalytics)
async def get_rule_analytics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get analytics overview for demographic rules.
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Total rules
        total_rules = db.query(DemographicRule).count()
        active_rules = db.query(DemographicRule).filter(
            DemographicRule.is_active == True
        ).count()
        
        # Average priority
        avg_priority = db.query(func.avg(DemographicRule.priority)).scalar() or 0.0
        
        # Rule effectiveness (mock data for now - would need real usage tracking)
        rules = db.query(DemographicRule).filter(
            DemographicRule.is_active == True
        ).limit(10).all()
        
        rule_effectiveness = []
        for rule in rules:
            # Get usage count
            usage_count = db.query(SurveyResponse).filter(
                SurveyResponse.demographic_rules_applied.contains([rule.id])
            ).count()
            
            # Calculate mock effectiveness metrics
            match_rate = min(0.8, usage_count / 100.0) if usage_count > 0 else 0.0
            impact_score = match_rate * rule.priority / 100.0
            
            rule_effectiveness.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "match_rate": match_rate,
                "impact_score": impact_score
            })
        
        # Sort by impact score
        rule_effectiveness.sort(key=lambda x: x["impact_score"], reverse=True)
        
        # Most used conditions (mock data)
        most_used_conditions = [
            {"field": "nationality", "operator": "eq", "usage_count": 15},
            {"field": "age", "operator": "gte", "usage_count": 12},
            {"field": "emirate", "operator": "in", "usage_count": 10},
            {"field": "employment_status", "operator": "eq", "usage_count": 8},
            {"field": "monthly_income", "operator": "gte", "usage_count": 6}
        ]
        
        return DemographicRuleAnalytics(
            total_rules=total_rules,
            active_rules=active_rules,
            average_priority=avg_priority,
            rule_effectiveness=rule_effectiveness,
            most_used_conditions=most_used_conditions,
            analysis_period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting rule analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving analytics"
        )


@router.post("/{rule_id}/activate")
async def activate_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Activate a demographic rule.
    """
    try:
        rule = db.query(DemographicRule).filter(
            DemographicRule.id == rule_id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demographic rule not found"
            )
        
        rule.is_active = True
        rule.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="activate_demographic_rule",
            entity_type="demographic_rule",
            entity_id=rule_id,
            details={"rule_name": rule.name}
        ))
        db.commit()
        
        return {"message": "Demographic rule activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating demographic rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error activating demographic rule"
        )


@router.post("/{rule_id}/deactivate")
async def deactivate_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Deactivate a demographic rule.
    """
    try:
        rule = db.query(DemographicRule).filter(
            DemographicRule.id == rule_id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demographic rule not found"
            )
        
        rule.is_active = False
        rule.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Log admin action
        db.add(AuditLog(
            user_id=admin_user.id,
            action="deactivate_demographic_rule",
            entity_type="demographic_rule",
            entity_id=rule_id,
            details={"rule_name": rule.name}
        ))
        db.commit()
        
        return {"message": "Demographic rule deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating demographic rule {rule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deactivating demographic rule"
        )