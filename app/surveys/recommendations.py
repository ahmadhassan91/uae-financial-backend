"""Recommendation engine for generating personalized financial advice."""
from typing import Dict, List, Any
from app.models import SurveyResponse, CustomerProfile


class RecommendationEngine:
    """Generate personalized recommendations based on survey responses and profile."""
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.recommendation_templates = self._load_recommendation_templates()
    
    def generate_recommendations(
        self, 
        survey_response: SurveyResponse, 
        customer_profile: CustomerProfile = None
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on survey and profile."""
        recommendations = []
        
        # Analyze each category and generate recommendations
        recommendations.extend(self._budgeting_recommendations(survey_response, customer_profile))
        recommendations.extend(self._savings_recommendations(survey_response, customer_profile))
        recommendations.extend(self._debt_recommendations(survey_response, customer_profile))
        recommendations.extend(self._planning_recommendations(survey_response, customer_profile))
        recommendations.extend(self._investment_recommendations(survey_response, customer_profile))
        
        # Sort by priority (1 = highest priority)
        recommendations.sort(key=lambda x: x['priority'])
        
        return recommendations
    
    def _budgeting_recommendations(
        self, 
        survey: SurveyResponse, 
        profile: CustomerProfile
    ) -> List[Dict[str, Any]]:
        """Generate budgeting-specific recommendations."""
        recommendations = []
        
        if survey.budgeting_score < 50:
            recommendations.append({
                'category': 'budgeting',
                'title': 'Create a Detailed Monthly Budget',
                'description': 'Start tracking your income and expenses to gain better control over your finances. A budget helps you understand where your money goes and identify areas for improvement.',
                'priority': 1,
                'action_steps': [
                    'List all sources of monthly income',
                    'Track all expenses for one month',
                    'Categorize expenses (housing, food, transportation, etc.)',
                    'Set spending limits for each category',
                    'Review and adjust monthly'
                ],
                'resources': [
                    {'type': 'app', 'name': 'Mint', 'url': 'https://mint.intuit.com'},
                    {'type': 'app', 'name': 'YNAB', 'url': 'https://youneedabudget.com'},
                    {'type': 'guide', 'name': 'UAE Banking Budget Tools', 'url': '#'}
                ],
                'expected_impact': 'high'
            })
        
        if survey.budgeting_score < 70:
            recommendations.append({
                'category': 'budgeting',
                'title': 'Use the 50/30/20 Rule',
                'description': 'Allocate 50% of income to needs, 30% to wants, and 20% to savings and debt repayment. This simple framework helps maintain financial balance.',
                'priority': 2,
                'action_steps': [
                    'Calculate your after-tax monthly income',
                    'Allocate 50% to essential expenses (rent, utilities, groceries)',
                    'Set aside 30% for discretionary spending',
                    'Dedicate 20% to savings and debt payments'
                ],
                'resources': [
                    {'type': 'calculator', 'name': '50/30/20 Calculator', 'url': '#'},
                    {'type': 'guide', 'name': 'UAE Budgeting Guide', 'url': '#'}
                ],
                'expected_impact': 'medium'
            })
        
        return recommendations
    
    def _savings_recommendations(
        self, 
        survey: SurveyResponse, 
        profile: CustomerProfile
    ) -> List[Dict[str, Any]]:
        """Generate savings-specific recommendations."""
        recommendations = []
        
        if survey.savings_score < 40:
            recommendations.append({
                'category': 'savings',
                'title': 'Build an Emergency Fund',
                'description': 'Start with saving AED 1,000 as your initial emergency fund, then work towards 3-6 months of expenses. This protects you from unexpected financial shocks.',
                'priority': 1,
                'action_steps': [
                    'Open a separate savings account for emergencies',
                    'Start with saving AED 100-200 monthly',
                    'Automate transfers to your emergency fund',
                    'Build up to AED 1,000 first milestone',
                    'Continue until you have 3-6 months of expenses'
                ],
                'resources': [
                    {'type': 'account', 'name': 'Emirates NBD Savings Account', 'url': '#'},
                    {'type': 'account', 'name': 'ADCB Savings Plus', 'url': '#'},
                    {'type': 'guide', 'name': 'Emergency Fund Guide', 'url': '#'}
                ],
                'expected_impact': 'high'
            })
        
        if survey.savings_score < 60:
            recommendations.append({
                'category': 'savings',
                'title': 'Automate Your Savings',
                'description': 'Set up automatic transfers to savings accounts to make saving effortless and consistent.',
                'priority': 2,
                'action_steps': [
                    'Set up automatic transfer on payday',
                    'Start with 10% of income if possible',
                    'Use separate accounts for different goals',
                    'Review and increase amounts quarterly'
                ],
                'resources': [
                    {'type': 'tool', 'name': 'Bank Auto-Transfer Setup', 'url': '#'},
                    {'type': 'app', 'name': 'Savings Goal Tracker', 'url': '#'}
                ],
                'expected_impact': 'medium'
            })
        
        return recommendations
    
    def _debt_recommendations(
        self, 
        survey: SurveyResponse, 
        profile: CustomerProfile
    ) -> List[Dict[str, Any]]:
        """Generate debt management recommendations."""
        recommendations = []
        
        if survey.debt_management_score < 50:
            recommendations.append({
                'category': 'debt_management',
                'title': 'Create a Debt Repayment Strategy',
                'description': 'List all debts and create a systematic repayment plan. Consider the debt snowball or avalanche method.',
                'priority': 1,
                'action_steps': [
                    'List all debts with balances and interest rates',
                    'Choose debt snowball (smallest first) or avalanche (highest interest first)',
                    'Make minimum payments on all debts',
                    'Put extra money toward target debt',
                    'Repeat until debt-free'
                ],
                'resources': [
                    {'type': 'calculator', 'name': 'Debt Payoff Calculator', 'url': '#'},
                    {'type': 'guide', 'name': 'UAE Debt Management Guide', 'url': '#'}
                ],
                'expected_impact': 'high'
            })
        
        if survey.debt_management_score < 70:
            recommendations.append({
                'category': 'debt_management',
                'title': 'Monitor Your Credit Score',
                'description': 'Regular credit monitoring helps you understand your creditworthiness and catch errors early.',
                'priority': 2,
                'action_steps': [
                    'Check your AECB credit report annually',
                    'Sign up for credit monitoring services',
                    'Pay all bills on time',
                    'Keep credit utilization below 30%'
                ],
                'resources': [
                    {'type': 'service', 'name': 'AECB Credit Report', 'url': 'https://www.aecb.gov.ae'},
                    {'type': 'app', 'name': 'Credit Monitor UAE', 'url': '#'}
                ],
                'expected_impact': 'medium'
            })
        
        return recommendations
    
    def _planning_recommendations(
        self, 
        survey: SurveyResponse, 
        profile: CustomerProfile
    ) -> List[Dict[str, Any]]:
        """Generate financial planning recommendations."""
        recommendations = []
        
        if survey.financial_planning_score < 50:
            recommendations.append({
                'category': 'financial_planning',
                'title': 'Set SMART Financial Goals',
                'description': 'Define Specific, Measurable, Achievable, Relevant, and Time-bound financial goals for the next 1, 5, and 10 years.',
                'priority': 1,
                'action_steps': [
                    'Write down your short-term goals (1 year)',
                    'Define medium-term goals (2-5 years)',
                    'Set long-term goals (5+ years)',
                    'Make each goal specific with target amounts',
                    'Create action plans for each goal'
                ],
                'resources': [
                    {'type': 'template', 'name': 'Goal Setting Worksheet', 'url': '#'},
                    {'type': 'tool', 'name': 'Financial Goal Calculator', 'url': '#'}
                ],
                'expected_impact': 'high'
            })
        
        # Age-specific recommendations (only if profile exists)
        if profile and profile.age < 35:
            recommendations.append({
                'category': 'financial_planning',
                'title': 'Start Retirement Planning Early',
                'description': 'Starting retirement savings in your 20s and 30s gives you the power of compound interest over decades.',
                'priority': 2,
                'action_steps': [
                    'Contribute to your company pension if available',
                    'Open a personal retirement account',
                    'Aim to save 10-15% of income for retirement',
                    'Consider low-cost index funds'
                ],
                'resources': [
                    {'type': 'guide', 'name': 'UAE Retirement Planning', 'url': '#'},
                    {'type': 'calculator', 'name': 'Retirement Calculator', 'url': '#'}
                ],
                'expected_impact': 'high'
            })
        
        return recommendations
    
    def _investment_recommendations(
        self, 
        survey: SurveyResponse, 
        profile: CustomerProfile
    ) -> List[Dict[str, Any]]:
        """Generate investment recommendations based on risk tolerance and knowledge."""
        recommendations = []
        
        if survey.investment_knowledge_score < 40:
            recommendations.append({
                'category': 'investment_knowledge',
                'title': 'Learn Investment Basics',
                'description': 'Build your investment knowledge before putting money at risk. Understanding basics helps you make better decisions.',
                'priority': 2,
                'action_steps': [
                    'Read about different investment types',
                    'Understand risk vs. return relationship',
                    'Learn about diversification',
                    'Study UAE investment options',
                    'Consider taking an investment course'
                ],
                'resources': [
                    {'type': 'course', 'name': 'Investment Fundamentals', 'url': '#'},
                    {'type': 'book', 'name': 'UAE Investment Guide', 'url': '#'},
                    {'type': 'website', 'name': 'Securities & Commodities Authority', 'url': 'https://www.sca.gov.ae'}
                ],
                'expected_impact': 'medium'
            })
        
        if survey.investment_knowledge_score >= 40 and survey.risk_tolerance == 'moderate':
            recommendations.append({
                'category': 'investment_knowledge',
                'title': 'Start with Index Funds',
                'description': 'Begin investing with low-cost, diversified index funds that track market performance. They offer good returns with moderate risk.',
                'priority': 2,
                'action_steps': [
                    'Open a brokerage account with a UAE bank',
                    'Research UAE and international index funds',
                    'Start with small monthly investments',
                    'Diversify across different markets',
                    'Review and rebalance quarterly'
                ],
                'resources': [
                    {'type': 'platform', 'name': 'Emirates NBD Investment', 'url': '#'},
                    {'type': 'platform', 'name': 'ADCB Securities', 'url': '#'},
                    {'type': 'guide', 'name': 'Index Fund Guide', 'url': '#'}
                ],
                'expected_impact': 'medium'
            })
        
        return recommendations
    
    def _load_recommendation_templates(self) -> Dict[str, Any]:
        """Load recommendation templates (could be from database or config)."""
        # This could be loaded from a database or configuration file
        # For now, we'll use the methods above to generate recommendations
        return {}
