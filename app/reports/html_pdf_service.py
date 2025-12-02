"""HTML-based PDF generation service for Financial Clinic reports."""
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from pathlib import Path
import io


class HTMLPDFService:
    """Service for generating PDF reports from HTML templates."""
    
    def __init__(self):
        """Initialize the HTML PDF service."""
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def _get_logo_base64(self, logo_path: str) -> str:
        """Convert logo file to base64 string."""
        try:
            with open(logo_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error loading logo {logo_path}: {e}")
            return ""
    
    def _translate_category(self, category: str, language: str) -> str:
        """Translate category name."""
        category_map = {
            'Income Stream': {'en': 'Income Stream', 'ar': 'تدفق الدخل'},
            'Monthly Expenses Management': {'en': 'Monthly Expenses Management', 'ar': 'إدارة النفقات الشهرية'},
            'Savings Habit': {'en': 'Saving Habits', 'ar': 'عادات الادخار'},
            'Emergency Savings': {'en': 'Emergency Savings', 'ar': 'مدخرات الطوارئ'},
            'Debt Management': {'en': 'Debt Management', 'ar': 'إدارة الديون'},
            'Retirement Planning': {'en': 'Retirement Planning', 'ar': 'التخطيط للتقاعد'},
            'Protecting Your Assets | Loved Ones': {'en': 'Protecting Your Assets | Loved Ones', 'ar': 'حماية أصولك | أحبائك'},
            'Planning for Your Future | Siblings': {'en': 'Planning for Your Future | Siblings', 'ar': 'التخطيط لمستقبلك | الأشقاء'},
            'Protecting Your Family': {'en': 'Protecting Your Family', 'ar': 'حماية عائلتك'}
        }
        
        category_data = category_map.get(category, {'en': category, 'ar': category})
        return category_data['ar'] if language == 'ar' else category_data['en']
    
    def _get_category_description(self, category: str, language: str) -> str:
        """Get category description."""
        descriptions = {
            'Income Stream': {
                'en': 'Do you have multiple sources of income?',
                'ar': 'هل لديك مصادر دخل متعددة؟'
            },
            'Monthly Expenses Management': {
                'en': 'How well do you manage your monthly expenses?',
                'ar': 'ما مدى جودة إدارتك لنفقاتك الشهرية؟'
            },
            'Savings Habit': {
                'en': 'Do you save regularly?',
                'ar': 'هل تدخر بانتظام؟'
            },
            'Emergency Savings': {
                'en': 'Can you handle unexpected expenses?',
                'ar': 'هل يمكنك التعامل مع النفقات غير المتوقعة؟'
            },
            'Debt Management': {
                'en': 'How well do you manage your debts?',
                'ar': 'ما مدى جودة إدارتك لديونك؟'
            },
            'Retirement Planning': {
                'en': 'Are you prepared for retirement?',
                'ar': 'هل أنت مستعد للتقاعد؟'
            },
            'Protecting Your Assets | Loved Ones': {
                'en': 'Is your family financially protected?',
                'ar': 'هل عائلتك محمية مالياً؟'
            },
            'Planning for Your Future | Siblings': {
                'en': 'Are you planning for your siblings\' future?',
                'ar': 'هل تخطط لمستقبل أشقائك؟'
            },
            'Protecting Your Family': {
                'en': 'Is your family financially protected?',
                'ar': 'هل عائلتك محمية مالياً؟'
            }
        }
        
        desc = descriptions.get(category, {'en': '', 'ar': ''})
        return desc['ar'] if language == 'ar' else desc['en']
    
    async def generate_financial_clinic_pdf(
        self,
        result_data: Dict[str, Any],
        language: str = "en",
        customer_name: str = ""
    ) -> bytes:
        """
        Generate PDF report from HTML template.
        
        Args:
            result_data: Financial clinic result data
            language: Language code ('en' or 'ar')
            customer_name: Customer name for personalization
            
        Returns:
            bytes: Generated PDF content
        """
        try:
            # Load template
            template = self.jinja_env.get_template('financial_clinic_pdf_template.html')
            
            # Get logo paths (adjust these paths based on your setup)
            frontend_path = Path(__file__).parent.parent.parent.parent / 'frontend' / 'public'
            financial_clinic_logo = frontend_path / 'homepage' / 'icons' / 'logo.svg'
            national_bonds_logo = frontend_path / 'homepage' / 'images' / 'nbc-logo2-02-1.png'
            
            # Convert logos to base64
            financial_clinic_logo_base64 = self._get_logo_base64(str(financial_clinic_logo))
            national_bonds_logo_base64 = self._get_logo_base64(str(national_bonds_logo))
            
            # Prepare category translations and descriptions
            category_translations = {}
            category_descriptions = {}
            for category_name in result_data.get('category_scores', {}).keys():
                category_translations[category_name] = self._translate_category(category_name, language)
                category_descriptions[category_name] = self._get_category_description(category_name, language)
            
            # Prepare insights with translated categories
            insights = []
            for insight in result_data.get('insights', []):
                insights.append({
                    'category_translated': self._translate_category(insight.get('category', ''), language),
                    'text': insight.get('text_ar' if language == 'ar' else 'text', insight.get('text', ''))
                })
            
            # Render HTML
            html_content = template.render(
                language=language,
                customer_name=customer_name,
                total_score=result_data.get('total_score', 0),
                category_scores=result_data.get('category_scores', {}),
                category_translations=category_translations,
                category_descriptions=category_descriptions,
                insights=insights,
                financial_clinic_logo_base64=financial_clinic_logo_base64,
                national_bonds_logo_base64=national_bonds_logo_base64,
                current_year=datetime.now().year
            )
            
            # Generate PDF from HTML using WeasyPrint
            pdf_bytes = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_bytes)
            pdf_content = pdf_bytes.getvalue()
            
            return pdf_content
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise Exception(f"Failed to generate PDF: {str(e)}")
