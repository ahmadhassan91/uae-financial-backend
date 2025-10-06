"""Survey scoring engine for calculating financial health scores.

This module implements the official 7-pillar financial health scoring methodology
that matches the frontend implementation exactly. The scoring uses weighted averages
based on question weights and converts Likert scale responses (1-5) to a final
score range of 15-75 (or 15-80 with conditional Q16).

Key Features:
- Pillar-based scoring structure matching frontend PILLAR_DEFINITIONS
- Weighted average calculation using question weights
- Conditional Q16 scoring for users with children
- Backward compatibility with legacy scoring format
"""
from typing import Dict, List, Tuple, Any, Optional
import json


class SurveyScorer:
    """Calculate financial health scores from survey responses."""
    
    def __init__(self):
        """Initialize the scoring engine with the official 7-pillar methodology."""
        # Pillar definitions matching frontend structure exactly
        self.PILLAR_DEFINITIONS = {
            'income_stream': {
                'name': 'Income Stream',
                'description': 'Stability and diversity of income sources',
                'questions': ['q1_income_stability', 'q2_income_sources'],
                'base_weight': 20  # 10% + 10% = 20%
            },
            'monthly_expenses': {
                'name': 'Monthly Expenses Management',
                'description': 'Budgeting and expense control',
                'questions': ['q3_living_expenses', 'q4_budget_tracking', 'q5_spending_control', 'q6_expense_review'],
                'base_weight': 25  # 10% + 5% + 5% + 5% = 25%
            },
            'savings_habit': {
                'name': 'Savings Habit',
                'description': 'Saving behavior and emergency preparedness',
                'questions': ['q7_savings_rate', 'q8_emergency_fund', 'q9_savings_optimization'],
                'base_weight': 15  # 5% + 5% + 5% = 15%
            },
            'debt_management': {
                'name': 'Debt Management',
                'description': 'Debt control and credit health',
                'questions': ['q10_payment_history', 'q11_debt_ratio', 'q12_credit_score'],
                'base_weight': 15  # 5% + 5% + 5% = 15%
            },
            'retirement_planning': {
                'name': 'Retirement Planning',
                'description': 'Long-term financial security',
                'questions': ['q13_retirement_planning'],
                'base_weight': 10  # 10%
            },
            'protection': {
                'name': 'Protection',
                'description': 'Insurance and risk management',
                'questions': ['q14_insurance_coverage'],
                'base_weight': 5   # 5%
            },
            'future_planning': {
                'name': 'Future Planning',
                'description': 'Financial planning and family preparation',
                'questions': ['q15_financial_planning', 'q16_children_planning'],
                'base_weight': 10  # 5% + 5% = 10% (15% if Q16 applies)
            }
        }
        
        # Question weights matching frontend exactly
        self.QUESTION_WEIGHTS = {
            # Income Stream (20% total)
            'q1_income_stability': 10,
            'q2_income_sources': 10,
            
            # Monthly Expenses Management (25% total)
            'q3_living_expenses': 10,
            'q4_budget_tracking': 5,
            'q5_spending_control': 5,
            'q6_expense_review': 5,
            
            # Savings Habit (15% total)
            'q7_savings_rate': 5,
            'q8_emergency_fund': 5,
            'q9_savings_optimization': 5,
            
            # Debt Management (15% total)
            'q10_payment_history': 5,
            'q11_debt_ratio': 5,
            'q12_credit_score': 5,
            
            # Retirement Planning (10% total)
            'q13_retirement_planning': 10,
            
            # Protection (5% total)
            'q14_insurance_coverage': 5,
            
            # Future Planning (5% base, 10% with Q16)
            'q15_financial_planning': 5,
            'q16_children_planning': 5  # Conditional question
        }
    
    def calculate_scores_v2(self, responses: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate financial health scores using weighted average methodology matching frontend exactly."""
        if profile is None:
            profile = {}
            
        # Create response map for quick lookup
        response_map = {q_id: value for q_id, value in responses.items()}
        
        # Check conditional Q16 logic
        has_children = profile.get('children') == 'Yes'
        
        # Calculate pillar scores using weighted averages
        pillar_scores = []
        weighted_sum = 0
        total_weight = 0
        
        for pillar_key, pillar_def in self.PILLAR_DEFINITIONS.items():
            pillar_score = 0
            pillar_question_count = 0
            pillar_weight = 0
            
            for question_id in pillar_def['questions']:
                # Skip Q16 if user doesn't have children
                if question_id == 'q16_children_planning' and not has_children:
                    continue
                    
                if question_id in response_map:
                    pillar_score += response_map[question_id]
                    pillar_question_count += 1
                    pillar_weight += self.QUESTION_WEIGHTS[question_id]
            
            if pillar_question_count > 0:
                avg_score = pillar_score / pillar_question_count
                weighted_score = avg_score * (pillar_weight / 100)
                
                weighted_sum += weighted_score
                total_weight += pillar_weight
                
                pillar_scores.append({
                    'factor': pillar_key,
                    'name': pillar_def['name'],
                    'score': round(avg_score, 2),
                    'max_score': 5,
                    'percentage': round((avg_score / 5) * 100),
                    'weight': pillar_weight
                })
        
        # Calculate total score (15-75 base, 15-80 if Q16 applies)
        base_score = 15
        max_score = 80 if has_children else 75
        score_range = max_score - base_score
        
        # Convert weighted average (1-5) to target range
        average_score = weighted_sum / (total_weight / 100) if total_weight > 0 else 1
        total_score = base_score + ((average_score - 1) / 4) * score_range
        
        return {
            'total_score': max(base_score, min(max_score, round(total_score))),
            'pillar_scores': pillar_scores,
            'max_possible_score': max_score,
            'weighted_sum': weighted_sum,
            'total_weight': total_weight,
            'average_score': average_score
        }
    
    def calculate_scores(self, responses: Dict[str, Any]) -> Dict[str, float]:
        """Legacy method for backward compatibility."""
        # Use the new method but return in old format for compatibility
        result = self.calculate_scores_v2(responses)
        
        # Convert to legacy format
        pillar_map = {}
        for pillar in result['pillar_scores']:
            pillar_map[f"{pillar['factor']}_score"] = pillar['score']
        
        # Convert pillar scores to match old expectations
        converted_scores = {
            'budgeting_score': round((pillar_map.get('income_stream_score', 0) + pillar_map.get('monthly_expenses_score', 0)) / 2 * 20, 2),
            'savings_score': round(pillar_map.get('savings_habit_score', 0) * 20, 2),
            'debt_management_score': round(pillar_map.get('debt_management_score', 0) * 20, 2),
            'financial_planning_score': round((pillar_map.get('retirement_planning_score', 0) + 
                                             pillar_map.get('protection_score', 0) + 
                                             pillar_map.get('future_planning_score', 0)) / 3 * 20, 2),
            'investment_knowledge_score': 0,  # Not part of the 7-pillar system
            'overall_score': round((result['total_score'] / result['max_possible_score']) * 100, 2)
        }
        
        return converted_scores
    
    def get_pillar_weight_calculation(self, pillar_key: str, has_children: bool = False) -> int:
        """Calculate the total weight for a pillar based on its questions."""
        pillar_def = self.PILLAR_DEFINITIONS.get(pillar_key)
        if not pillar_def:
            return 0
            
        total_weight = 0
        for question_id in pillar_def['questions']:
            # Skip Q16 if user doesn't have children
            if question_id == 'q16_children_planning' and not has_children:
                continue
            total_weight += self.QUESTION_WEIGHTS.get(question_id, 0)
            
        return total_weight
    
    def get_total_possible_weight(self, has_children: bool = False) -> int:
        """Calculate the total possible weight for all pillars."""
        total = 0
        for pillar_key in self.PILLAR_DEFINITIONS.keys():
            total += self.get_pillar_weight_calculation(pillar_key, has_children)
        return total
    
    def get_question_weight(self, question_id: str) -> int:
        """Get the weight for a specific question."""
        return self.QUESTION_WEIGHTS.get(question_id, 0)
    
    def get_pillar_questions(self, pillar_key: str) -> List[str]:
        """Get all questions for a specific pillar."""
        pillar_def = self.PILLAR_DEFINITIONS.get(pillar_key)
        if not pillar_def:
            return []
        return pillar_def['questions'].copy()
    
    def validate_response_value(self, value: Any) -> bool:
        """Validate that a response value is within the expected Likert scale range (1-5)."""
        try:
            numeric_value = float(value)
            return 1 <= numeric_value <= 5
        except (ValueError, TypeError):
            return False
    
    def determine_risk_tolerance(self, responses: Dict[str, Any]) -> str:
        """Determine risk tolerance based on survey responses."""
        risk_indicators = []
        
        # Check emergency fund (affects risk capacity)
        if 'q8_emergency_fund' in responses:
            fund_score = float(responses.get('q8_emergency_fund', 3))
            if fund_score >= 4:  # 3-6 months or more
                risk_indicators.append('high')
            elif fund_score <= 2:  # 1 month or less
                risk_indicators.append('low')
            else:
                risk_indicators.append('moderate')
        
        # Check debt management (affects risk capacity)
        if 'q11_debt_ratio' in responses:
            debt_score = float(responses.get('q11_debt_ratio', 3))
            if debt_score >= 4:  # Low debt ratio
                risk_indicators.append('high')
            elif debt_score <= 2:  # High debt ratio
                risk_indicators.append('low')
            else:
                risk_indicators.append('moderate')
        
        # Check savings habit (affects risk capacity)
        if 'q7_savings_rate' in responses:
            savings_score = float(responses.get('q7_savings_rate', 3))
            if savings_score >= 4:  # High savings rate
                risk_indicators.append('high')
            elif savings_score <= 2:  # Low savings rate
                risk_indicators.append('low')
            else:
                risk_indicators.append('moderate')
        
        # Default to moderate if no indicators
        if not risk_indicators:
            return 'moderate'
        
        # Determine overall risk tolerance
        risk_counts = {'low': 0, 'moderate': 0, 'high': 0}
        for indicator in risk_indicators:
            risk_counts[indicator] += 1
        
        return max(risk_counts, key=risk_counts.get)
    
    def extract_financial_goals(self, responses: Dict[str, Any]) -> List[str]:
        """Extract financial goals from survey responses."""
        goals = []
        
        # Check various goal-related questions
        goal_questions = [
            'financial_goals', 'short_term_goals', 'long_term_goals',
            'retirement_goals', 'savings_goals'
        ]
        
        for question in goal_questions:
            if question in responses:
                answer = responses[question]
                if isinstance(answer, list):
                    goals.extend(answer)
                elif isinstance(answer, str) and answer.strip():
                    goals.append(answer)
        
        # Remove duplicates and empty goals
        return list(set(goal for goal in goals if goal and goal.strip()))
