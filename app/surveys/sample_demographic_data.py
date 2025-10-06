"""
Sample demographic rules and question variations for testing and initial setup.

This module provides sample data to demonstrate the dynamic question engine
capabilities with realistic UAE-specific demographic rules and variations.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import DemographicRule, QuestionVariation


def create_sample_demographic_rules(db: Session) -> List[DemographicRule]:
    """Create sample demographic rules for UAE financial health assessment."""
    
    sample_rules = [
        {
            'name': 'UAE Citizens - Islamic Finance Focus',
            'description': 'Show Islamic finance questions to UAE citizens who prefer Sharia-compliant products',
            'conditions': {
                'and': [
                    {'nationality': {'eq': 'UAE'}},
                    {'islamic_finance_preference': {'eq': True}}
                ]
            },
            'actions': {
                'include_questions': ['q1_income_stability_islamic', 'q9_savings_optimization_islamic'],
                'add_questions': ['q17_zakat_planning', 'q18_islamic_investment']
            },
            'priority': 10
        },
        {
            'name': 'Expatriates - International Banking',
            'description': 'Focus on international banking and remittance questions for expatriates',
            'conditions': {
                'and': [
                    {'nationality': {'ne': 'UAE'}},
                    {'years_in_uae': {'gte': 1}}
                ]
            },
            'actions': {
                'include_questions': ['q1_income_stability_expat', 'q2_income_sources_expat'],
                'add_questions': ['q19_remittance_planning', 'q20_visa_financial_planning']
            },
            'priority': 20
        },
        {
            'name': 'High Income Earners - Investment Focus',
            'description': 'Advanced investment questions for high-income individuals',
            'conditions': {
                'or': [
                    {'monthly_income': {'in': ['50000-100000', '100000+']}},
                    {'investment_experience': {'in': ['Advanced', 'Expert']}}
                ]
            },
            'actions': {
                'include_questions': ['q9_savings_optimization_advanced'],
                'add_questions': ['q21_portfolio_diversification', 'q22_tax_optimization']
            },
            'priority': 30
        },
        {
            'name': 'Young Professionals - Career Start',
            'description': 'Focus on basic financial planning for young professionals',
            'conditions': {
                'and': [
                    {'age': {'lte': 30}},
                    {'employment_status': {'eq': 'Employed'}},
                    {'years_in_uae': {'lte': 5}}
                ]
            },
            'actions': {
                'include_questions': ['q7_savings_rate_starter', 'q8_emergency_fund_basic'],
                'exclude_questions': ['q13_retirement_planning']
            },
            'priority': 40
        },
        {
            'name': 'Dubai/Abu Dhabi Residents - Premium Services',
            'description': 'Premium banking questions for major emirate residents',
            'conditions': {
                'and': [
                    {'emirate': {'in': ['Dubai', 'Abu Dhabi']}},
                    {'monthly_income': {'gte': '20000'}}
                ]
            },
            'actions': {
                'include_questions': ['q12_credit_score_premium'],
                'add_questions': ['q23_premium_banking', 'q24_wealth_management']
            },
            'priority': 50
        },
        {
            'name': 'Parents - Children Education Planning',
            'description': 'Enhanced children planning questions for parents',
            'conditions': {
                'children': {'eq': 'Yes'}
            },
            'actions': {
                'include_questions': ['q16_children_planning_enhanced'],
                'add_questions': ['q25_education_savings', 'q26_children_insurance']
            },
            'priority': 15
        }
    ]
    
    created_rules = []
    
    for rule_data in sample_rules:
        # Check if rule already exists
        existing = db.query(DemographicRule).filter(
            DemographicRule.name == rule_data['name']
        ).first()
        
        if not existing:
            rule = DemographicRule(
                name=rule_data['name'],
                description=rule_data['description'],
                conditions=rule_data['conditions'],
                actions=rule_data['actions'],
                priority=rule_data['priority'],
                is_active=True
            )
            
            db.add(rule)
            created_rules.append(rule)
    
    db.commit()
    return created_rules


def create_sample_question_variations(db: Session) -> List[QuestionVariation]:
    """Create sample question variations for different demographic groups."""
    
    sample_variations = [
        {
            'base_question_id': 'q1_income_stability',
            'variation_name': 'islamic_version',
            'language': 'en',
            'text': 'My halal income is stable and predictable each month.',
            'options': [
                {'value': 5, 'label': 'Strongly Agree'},
                {'value': 4, 'label': 'Agree'},
                {'value': 3, 'label': 'Neutral'},
                {'value': 2, 'label': 'Disagree'},
                {'value': 1, 'label': 'Strongly Disagree'}
            ],
            'demographic_rules': {
                'and': [
                    {'nationality': {'eq': 'UAE'}},
                    {'islamic_finance_preference': {'eq': True}}
                ]
            },
            'factor': 'income_stream',
            'weight': 10
        },
        {
            'base_question_id': 'q1_income_stability',
            'variation_name': 'expat_version',
            'language': 'en',
            'text': 'My income is stable and predictable each month, considering currency fluctuations.',
            'options': [
                {'value': 5, 'label': 'Very stable, no currency concerns'},
                {'value': 4, 'label': 'Mostly stable with minor fluctuations'},
                {'value': 3, 'label': 'Somewhat affected by currency changes'},
                {'value': 2, 'label': 'Frequently affected by currency changes'},
                {'value': 1, 'label': 'Highly unstable due to currency issues'}
            ],
            'demographic_rules': {
                'nationality': {'ne': 'UAE'}
            },
            'factor': 'income_stream',
            'weight': 10
        },
        {
            'base_question_id': 'q2_income_sources',
            'variation_name': 'expat_version',
            'language': 'en',
            'text': 'I have multiple income sources, including potential income from my home country.',
            'options': [
                {'value': 5, 'label': 'Multiple sources in UAE and home country'},
                {'value': 4, 'label': 'Multiple sources primarily in UAE'},
                {'value': 3, 'label': 'UAE salary plus home country investments'},
                {'value': 2, 'label': 'UAE salary plus occasional home income'},
                {'value': 1, 'label': 'Only UAE salary'}
            ],
            'demographic_rules': {
                'nationality': {'ne': 'UAE'}
            },
            'factor': 'income_stream',
            'weight': 10
        },
        {
            'base_question_id': 'q7_savings_rate',
            'variation_name': 'starter_version',
            'language': 'en',
            'text': 'I save from my income every month, even if it\'s a small amount.',
            'options': [
                {'value': 5, 'label': '10% or more'},
                {'value': 4, 'label': '5-10%'},
                {'value': 3, 'label': '2-5%'},
                {'value': 2, 'label': 'Less than 2%'},
                {'value': 1, 'label': '0% - I spend everything'}
            ],
            'demographic_rules': {
                'and': [
                    {'age': {'lte': 30}},
                    {'years_in_uae': {'lte': 5}}
                ]
            },
            'factor': 'savings_habit',
            'weight': 5
        },
        {
            'base_question_id': 'q8_emergency_fund',
            'variation_name': 'basic_version',
            'language': 'en',
            'text': 'I have money set aside for unexpected expenses.',
            'options': [
                {'value': 5, 'label': '3+ months of expenses'},
                {'value': 4, 'label': '1-3 months of expenses'},
                {'value': 3, 'label': 'Some savings for emergencies'},
                {'value': 2, 'label': 'Very little emergency money'},
                {'value': 1, 'label': 'No emergency savings'}
            ],
            'demographic_rules': {
                'and': [
                    {'age': {'lte': 30}},
                    {'employment_status': {'eq': 'Employed'}}
                ]
            },
            'factor': 'savings_habit',
            'weight': 5
        },
        {
            'base_question_id': 'q9_savings_optimization',
            'variation_name': 'islamic_version',
            'language': 'en',
            'text': 'I keep my savings in Sharia-compliant, return-generating accounts or investments.',
            'options': [
                {'value': 5, 'label': 'Islamic investments with consistent returns'},
                {'value': 4, 'label': 'Islamic savings with good returns'},
                {'value': 3, 'label': 'Islamic savings account with minimal returns'},
                {'value': 2, 'label': 'Regular savings account (working on Islamic options)'},
                {'value': 1, 'label': 'Cash or non-Islamic accounts'}
            ],
            'demographic_rules': {
                'islamic_finance_preference': {'eq': True}
            },
            'factor': 'savings_habit',
            'weight': 5
        },
        {
            'base_question_id': 'q9_savings_optimization',
            'variation_name': 'advanced_version',
            'language': 'en',
            'text': 'I actively optimize my investment portfolio for maximum risk-adjusted returns.',
            'options': [
                {'value': 5, 'label': 'Sophisticated portfolio with regular rebalancing'},
                {'value': 4, 'label': 'Diversified investments with periodic review'},
                {'value': 3, 'label': 'Basic investment portfolio'},
                {'value': 2, 'label': 'Simple savings with some investments'},
                {'value': 1, 'label': 'Only basic savings accounts'}
            ],
            'demographic_rules': {
                'or': [
                    {'monthly_income': {'in': ['50000-100000', '100000+']}},
                    {'investment_experience': {'in': ['Advanced', 'Expert']}}
                ]
            },
            'factor': 'savings_habit',
            'weight': 5
        },
        {
            'base_question_id': 'q12_credit_score',
            'variation_name': 'premium_version',
            'language': 'en',
            'text': 'I actively manage my credit score and use premium banking services to optimize it.',
            'options': [
                {'value': 5, 'label': 'Excellent score with premium banking relationship'},
                {'value': 4, 'label': 'Good score with regular monitoring'},
                {'value': 3, 'label': 'Fair score with basic monitoring'},
                {'value': 2, 'label': 'Limited understanding but working to improve'},
                {'value': 1, 'label': 'No active credit score management'}
            ],
            'demographic_rules': {
                'and': [
                    {'emirate': {'in': ['Dubai', 'Abu Dhabi']}},
                    {'monthly_income': {'gte': '20000'}}
                ]
            },
            'factor': 'debt_management',
            'weight': 5
        },
        {
            'base_question_id': 'q16_children_planning',
            'variation_name': 'enhanced_version',
            'language': 'en',
            'text': 'I have comprehensive financial planning for my children\'s education, healthcare, and future.',
            'options': [
                {'value': 5, 'label': 'Complete planning with education insurance and investments'},
                {'value': 4, 'label': 'Good planning covering education and basic needs'},
                {'value': 3, 'label': 'Basic education savings and insurance'},
                {'value': 2, 'label': 'Some savings but limited planning'},
                {'value': 1, 'label': 'No specific children financial planning'}
            ],
            'demographic_rules': {
                'children': {'eq': 'Yes'}
            },
            'factor': 'future_planning',
            'weight': 5
        }
    ]
    
    # Arabic variations
    arabic_variations = [
        {
            'base_question_id': 'q1_income_stability',
            'variation_name': 'standard_arabic',
            'language': 'ar',
            'text': 'دخلي مستقر ويمكن التنبؤ به كل شهر.',
            'options': [
                {'value': 5, 'label': 'أوافق بشدة'},
                {'value': 4, 'label': 'أوافق'},
                {'value': 3, 'label': 'محايد'},
                {'value': 2, 'label': 'لا أوافق'},
                {'value': 1, 'label': 'لا أوافق بشدة'}
            ],
            'factor': 'income_stream',
            'weight': 10
        },
        {
            'base_question_id': 'q7_savings_rate',
            'variation_name': 'standard_arabic',
            'language': 'ar',
            'text': 'أدخر من دخلي كل شهر.',
            'options': [
                {'value': 5, 'label': '20% أو أكثر'},
                {'value': 4, 'label': 'أقل من 20%'},
                {'value': 3, 'label': 'أقل من 10%'},
                {'value': 2, 'label': '5% أو أقل'},
                {'value': 1, 'label': '0%'}
            ],
            'factor': 'savings_habit',
            'weight': 5
        },
        {
            'base_question_id': 'q9_savings_optimization',
            'variation_name': 'islamic_arabic',
            'language': 'ar',
            'text': 'أحتفظ بمدخراتي في حسابات أو استثمارات متوافقة مع الشريعة الإسلامية.',
            'options': [
                {'value': 5, 'label': 'استثمارات إسلامية مع عوائد ثابتة'},
                {'value': 4, 'label': 'مدخرات إسلامية مع عوائد جيدة'},
                {'value': 3, 'label': 'حساب توفير إسلامي مع عوائد قليلة'},
                {'value': 2, 'label': 'حساب توفير عادي (أعمل على الخيارات الإسلامية)'},
                {'value': 1, 'label': 'نقد أو حسابات غير إسلامية'}
            ],
            'demographic_rules': {
                'islamic_finance_preference': {'eq': True}
            },
            'factor': 'savings_habit',
            'weight': 5
        }
    ]
    
    # Combine all variations
    all_variations = sample_variations + arabic_variations
    
    created_variations = []
    
    for var_data in all_variations:
        # Check if variation already exists
        existing = db.query(QuestionVariation).filter(
            QuestionVariation.base_question_id == var_data['base_question_id'],
            QuestionVariation.variation_name == var_data['variation_name'],
            QuestionVariation.language == var_data['language']
        ).first()
        
        if not existing:
            variation = QuestionVariation(
                base_question_id=var_data['base_question_id'],
                variation_name=var_data['variation_name'],
                language=var_data['language'],
                text=var_data['text'],
                options=var_data['options'],
                demographic_rules=var_data.get('demographic_rules'),
                company_ids=var_data.get('company_ids'),
                factor=var_data['factor'],
                weight=var_data['weight'],
                is_active=True
            )
            
            db.add(variation)
            created_variations.append(variation)
    
    db.commit()
    return created_variations


def create_additional_questions_data(db: Session) -> Dict[str, Any]:
    """Create additional question definitions for new questions referenced in rules."""
    
    # These would be additional questions that can be added by demographic rules
    additional_questions = {
        'q17_zakat_planning': {
            'id': 'q17_zakat_planning',
            'question_number': 17,
            'text': 'I calculate and pay my Zakat obligations regularly.',
            'type': 'likert',
            'options': [
                {'value': 5, 'label': 'Always calculate and pay on time'},
                {'value': 4, 'label': 'Usually calculate and pay'},
                {'value': 3, 'label': 'Sometimes calculate and pay'},
                {'value': 2, 'label': 'Rarely calculate or pay'},
                {'value': 1, 'label': 'Do not calculate or pay Zakat'}
            ],
            'required': False,
            'factor': 'future_planning',
            'weight': 3,
            'conditional': True
        },
        'q18_islamic_investment': {
            'id': 'q18_islamic_investment',
            'question_number': 18,
            'text': 'I actively seek Sharia-compliant investment opportunities.',
            'type': 'likert',
            'options': [
                {'value': 5, 'label': 'Exclusively invest in Islamic products'},
                {'value': 4, 'label': 'Prefer Islamic investments when available'},
                {'value': 3, 'label': 'Consider Islamic investments occasionally'},
                {'value': 2, 'label': 'Limited knowledge of Islamic investments'},
                {'value': 1, 'label': 'Do not consider Islamic investments'}
            ],
            'required': False,
            'factor': 'savings_habit',
            'weight': 3,
            'conditional': True
        },
        'q19_remittance_planning': {
            'id': 'q19_remittance_planning',
            'question_number': 19,
            'text': 'I have a structured plan for sending money to my home country.',
            'type': 'likert',
            'options': [
                {'value': 5, 'label': 'Regular planned remittances with optimal rates'},
                {'value': 4, 'label': 'Regular remittances with rate monitoring'},
                {'value': 3, 'label': 'Occasional remittances as needed'},
                {'value': 2, 'label': 'Irregular remittances without planning'},
                {'value': 1, 'label': 'No structured remittance plan'}
            ],
            'required': False,
            'factor': 'monthly_expenses',
            'weight': 3,
            'conditional': True
        },
        'q20_visa_financial_planning': {
            'id': 'q20_visa_financial_planning',
            'question_number': 20,
            'text': 'I maintain adequate funds for visa renewals and potential relocation.',
            'type': 'likert',
            'options': [
                {'value': 5, 'label': 'Always maintain required funds plus buffer'},
                {'value': 4, 'label': 'Usually have required funds available'},
                {'value': 3, 'label': 'Sometimes have funds ready'},
                {'value': 2, 'label': 'Struggle to maintain required funds'},
                {'value': 1, 'label': 'No specific planning for visa costs'}
            ],
            'required': False,
            'factor': 'future_planning',
            'weight': 3,
            'conditional': True
        }
    }
    
    return additional_questions


def populate_sample_data(db: Session) -> Dict[str, Any]:
    """Populate database with sample demographic rules and question variations."""
    
    try:
        # Create demographic rules
        rules = create_sample_demographic_rules(db)
        
        # Create question variations
        variations = create_sample_question_variations(db)
        
        # Get additional questions data
        additional_questions = create_additional_questions_data(db)
        
        return {
            'success': True,
            'demographic_rules_created': len(rules),
            'question_variations_created': len(variations),
            'additional_questions_defined': len(additional_questions),
            'message': 'Sample demographic data populated successfully'
        }
        
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to populate sample data'
        }


if __name__ == "__main__":
    # This can be run as a script to populate sample data
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        result = populate_sample_data(db)
        print(f"Result: {result}")
    finally:
        db.close()