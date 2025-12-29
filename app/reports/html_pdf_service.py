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
    
    def _get_score_color(self, score: float) -> str:
        """
        Get color based on score range.
        Matches frontend color scheme from FinancialClinicResults.tsx
        
        Args:
            score: Score value (0-100)
            
        Returns:
            Hex color code
        """
        if score >= 80:
            return '#6cc922'  # Excellent - Green
        elif score >= 60:
            return '#fca924'  # Good - Yellow/Orange
        elif score >= 30:
            return '#fe6521'  # Fair - Orange
        else:
            return '#f00c01'  # Needs Improvement - Red
    
    def _get_status_label(self, score: float, language: str) -> str:
        """Get status label based on score."""
        if score >= 80:
            return 'ممتاز' if language == 'ar' else 'EXCELLENT'
        elif score >= 60:
            return 'جيد' if language == 'ar' else 'GOOD'
        elif score >= 30:
            return 'مقبول' if language == 'ar' else 'FAIR'
        else:
            return 'يحتاج إلى تحسين' if language == 'ar' else 'NEEDS IMPROVEMENT'
    
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
        # Strip whitespace and normalize language parameter (critical fix for production)
        language = language.strip().lower() if language else "en"
        
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Load template
            template = self.jinja_env.get_template('financial_clinic_pdf_template.html')
            
            # Use local SVG logo files from backend static directory
            import os
            
            # Get the static logos directory path
            static_logos_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')
            national_bonds_logo_path = os.path.join(static_logos_dir, 'NATIONAL BONDS LOGO.svg')
            financial_clinic_logo_path = os.path.join(static_logos_dir, 'financial-clinic-logo.svg')
            
            try:
                # Read National Bonds SVG logo
                if os.path.exists(national_bonds_logo_path):
                    with open(national_bonds_logo_path, 'rb') as f:
                        national_bonds_logo_base64 = base64.b64encode(f.read()).decode('utf-8')
                else:
                    logger.warning(f"National Bonds logo not found at: {national_bonds_logo_path}")
                    national_bonds_logo_base64 = ""
                
                # Read Financial Clinic SVG logo
                if os.path.exists(financial_clinic_logo_path):
                    with open(financial_clinic_logo_path, 'rb') as f:
                        financial_clinic_logo_base64 = base64.b64encode(f.read()).decode('utf-8')
                else:
                    logger.warning(f"Financial Clinic logo not found at: {financial_clinic_logo_path}")
                    financial_clinic_logo_base64 = ""
                    
            except Exception as logo_error:
                logger.error(f"Error loading logos: {logo_error}")
                financial_clinic_logo_base64 = ""
                national_bonds_logo_base64 = ""
            
            # Prepare category translations, descriptions, and colors
            category_translations = {}
            category_descriptions = {}
            category_colors = {}
            for category_name in result_data.get('category_scores', {}).keys():
                category_translations[category_name] = self._translate_category(category_name, language)
                category_descriptions[category_name] = self._get_category_description(category_name, language)
                
                # Calculate color based on category percentage
                category_data = result_data.get('category_scores', {}).get(category_name, {})
                percentage = (category_data.get('score', 0) / category_data.get('max_possible', 1)) * 100
                
                if percentage >= 70:
                    category_color = '#10b981'  # Green for good
                elif percentage >= 40:
                    category_color = '#f97316'  # Orange for fair
                else:
                    category_color = '#dc2626'  # Red for needs improvement
                
                category_colors[category_name] = category_color
            
            # Prepare insights with translated categories
            insights = []
            for insight in result_data.get('insights', []):
                insights.append({
                    'category_translated': self._translate_category(insight.get('category', ''), language),
                    'text': insight.get('text_ar' if language == 'ar' else 'text', insight.get('text', ''))
                })
            
            # Calculate status color and label based on score
            total_score = result_data.get('total_score', 0)
            if total_score >= 80:
                status_color = '#10b981'  # Green for Excellent
                status_label_en = 'EXCELLENT'
                status_label_ar = 'ممتاز'
            elif total_score >= 60:
                status_color = '#fbbf24'  # Yellow for Good
                status_label_en = 'GOOD'
                status_label_ar = 'جيد'
            elif total_score >= 30:
                status_color = '#f97316'  # Orange for Fair
                status_label_en = 'FAIR'
                status_label_ar = 'مقبول'
            else:
                status_color = '#dc2626'  # Red for Needs Improvement
                status_label_en = 'NEEDS IMPROVEMENT'
                status_label_ar = 'يحتاج إلى تحسين'
            
            status_label = status_label_ar if language == 'ar' else status_label_en
            
            # Render HTML
            html_content = template.render(
                language=language,
                customer_name=customer_name,
                total_score=total_score,
                status_color=status_color,
                status_label=status_label,
                category_scores=result_data.get('category_scores', {}),
                category_translations=category_translations,
                category_descriptions=category_descriptions,
                category_colors=category_colors,
                insights=insights,
                financial_clinic_logo_base64=financial_clinic_logo_base64,
                national_bonds_logo_base64=national_bonds_logo_base64,
                current_year=datetime.now().year
            )
            
            # Generate PDF from HTML using WeasyPrint with enhanced error handling
            pdf_bytes = io.BytesIO()
            
            try:
                # Configure WeasyPrint to handle SSL issues and Arabic text
                import os
                # Disable SSL verification for WeasyPrint (on-prem environments)
                os.environ['CURL_CA_BUNDLE'] = ''
                os.environ['SSL_VERIFY'] = 'false'
                
                from weasyprint import HTML, CSS
                from weasyprint.text.fonts import FontConfiguration
                
                font_config = FontConfiguration()
                
                # Add robust CSS for Arabic font support with fallbacks
                css_content = """
                    @page {
                        size: A4;
                        margin: 8mm;
                    }
                    
                    body {
                        font-family: Arial, sans-serif !important;
                        line-height: 1.4;
                        color: #333;
                    }
                    
                    body[lang="ar"] {
                        font-family: Arial, "Arial Unicode MS", Tahoma, sans-serif !important;
                        text-align: right;
                    }
                    
                    body[lang="en"] {
                        font-family: Arial, Helvetica, sans-serif !important;
                        text-align: left;
                    }
                    
                    .rtl {
                        text-align: right;
                        font-family: Arial, "Arial Unicode MS", Tahoma, sans-serif !important;
                    }
                    
                    /* Remove problematic external font references */
                    * {
                        font-family: Arial, sans-serif !important;
                    }
                """
                
                # Clean HTML content to remove problematic font references
                cleaned_html = html_content.replace('"Tajawal"', '"Arial"').replace('"Almarai"', '"Arial"')
                
                css_arabic = CSS(string=css_content, font_config=font_config)
                
                # Create HTML with cleaned content
                html_doc = HTML(string=cleaned_html, base_url='.')
                
                # Generate PDF with font configuration and Arabic support
                html_doc.write_pdf(
                    pdf_bytes,
                    stylesheets=[css_arabic],
                    font_config=font_config,
                    optimize_images=False,  # Disable image optimization to prevent issues
                    presentational_hints=True
                )
                
            except Exception as weasy_error:
                logger.error(f"WeasyPrint error: {str(weasy_error)}")
                
                # Fallback: Try with minimal CSS and no external fonts
                try:
                    simple_css = CSS(string="""
                        @page { size: A4; margin: 10mm; }
                        body { font-family: Arial, sans-serif; font-size: 12px; line-height: 1.4; }
                        .rtl { text-align: right; }
                    """)
                    
                    # Strip all complex styling and use only basic fonts
                    basic_html = html_content.replace('"Tajawal"', '"Arial"').replace('"Almarai"', '"Arial"')
                    basic_html = basic_html.replace('font-family: "Tajawal"', 'font-family: Arial')
                    basic_html = basic_html.replace('font-family: "Almarai"', 'font-family: Arial')
                    
                    HTML(string=basic_html).write_pdf(pdf_bytes, stylesheets=[simple_css])
                    logger.info("PDF generated successfully with fallback method")
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback PDF generation failed: {str(fallback_error)}")
                    raise Exception(f"PDF generation failed: WeasyPrint error: {str(weasy_error)}, Fallback error: {str(fallback_error)}")
            pdf_content = pdf_bytes.getvalue()
            
            return pdf_content
            
        except Exception as e:
            import traceback
            print(f"Error generating PDF: {e}")
            print(traceback.format_exc())
            raise Exception(f"Failed to generate PDF: {str(e)}")
