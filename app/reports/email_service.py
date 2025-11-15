"""Email service for delivering financial health reports."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template

from app.models import SurveyResponse, CustomerProfile, ReportDelivery
from app.config import settings


class EmailReportService:
    """Service for sending financial health reports via email."""
    
    def __init__(self):
        """Initialize the email service."""
        self.smtp_server = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@nationalbonds.ae')
        self.from_name = getattr(settings, 'FROM_NAME', 'National Bonds')
        
        # Set up Jinja2 environment for email templates
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        if os.path.exists(template_dir):
            self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        else:
            self.jinja_env = None
    
    async def send_report_email(
        self,
        recipient_email: str,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        pdf_content: bytes,
        language: str = "en",
        branding_config: Optional[Dict[str, Any]] = None,
        download_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a financial health report via email with download link."""
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            
            # Set email headers
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            
            # Set subject based on language
            if language == "ar":
                msg['Subject'] = "تقرير الصحة المالية الخاص بك جاهز!"
            else:
                msg['Subject'] = "Your Financial Health Report is Ready!"
            
            # Generate email content with download URL
            html_content = self._generate_email_html(
                survey_response, customer_profile, language, branding_config, download_url
            )
            text_content = self._generate_email_text(
                survey_response, customer_profile, language, download_url
            )
            
            # Attach HTML and text versions
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # Note: PDF is NOT attached - user downloads from link
            # This reduces email size and improves deliverability
            
            # Send email
            delivery_result = self._send_email(msg)
            
            return {
                'success': delivery_result['success'],
                'message': delivery_result['message'],
                'recipient': recipient_email,
                'subject': msg['Subject'],
                'download_url': download_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to send email: {str(e)}",
                'recipient': recipient_email,
                'error': str(e)
            }
    
    def _send_email(self, msg: MIMEMultipart) -> Dict[str, Any]:
        """Send email using SMTP."""
        try:
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            
            # Login if credentials are provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, msg['To'], text)
            server.quit()
            
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"SMTP error: {str(e)}"
            }
    
    def _generate_email_html(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str,
        branding_config: Optional[Dict[str, Any]] = None,
        download_url: Optional[str] = None
    ) -> str:
        """Generate HTML email content."""
        # Get base URL for assets (frontend URL)
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # Try to use the new Financial Clinic email template
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template('financial_clinic_email_template.html')
                
                # Prepare products list (can be customized based on score)
                products = self._get_recommended_products(survey_response, language)
                
                return template.render(
                    language=language,
                    customer_name=customer_profile.first_name if customer_profile else "Valued Customer",
                    overall_score=int(survey_response.overall_score) if survey_response.overall_score else 0,
                    download_url=download_url or "#",
                    products=products,
                    base_url=base_url,
                    current_year=datetime.now().year,
                    branding_config=branding_config or {}
                )
            except Exception as e:
                print(f"Template error: {e}")
                pass  # Fall back to inline template
        
        # Fallback to inline HTML template
        return self._get_inline_html_template(survey_response, customer_profile, language, branding_config, download_url)
    
    def _generate_email_text(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str,
        download_url: Optional[str] = None
    ) -> str:
        """Generate plain text email content."""
        download_text = f"\n\nDownload your report: {download_url}\n" if download_url else ""
        
        if language == "ar":
            return f"""
مرحباً {customer_profile.first_name if customer_profile else ""},

تهانينا! لقد أكملت للتو فحص صحتك المالية!

نتيجتك الإجمالية: {int(survey_response.overall_score) if survey_response.overall_score else 0}/100

تقريرك الشخصي للصحة المالية جاهز، ويتضمن:
✓ نتيجة الصحة المالية: تفصيل شفاف لأدائك في المجالات الرئيسية
✓ توصيات شخصية: طرق بسيطة وقابلة للتنفيذ لتحسين نتيجتك
✓ خطة عمل 90 يوماً: خطوات واضحة لبناء مستقبل مالي أقوى
{download_text if download_url else ""}
لأي استفسارات، يرجى زيارة موقعنا: www.nationalbonds.ae

مع أطيب التحيات,
فريق السندات الوطنية
"""
        else:
            return f"""
Hello {customer_profile.first_name if customer_profile else ""},

Congratulations—you've just completed your Financial Checkup!

Your Overall Score: {int(survey_response.overall_score) if survey_response.overall_score else 0}/100

Your personalized Financial Health Report is ready, including:
✓ Your Financial Health Score: a transparent breakdown of your performance
✓ Personalized Recommendations: simple, actionable ways to improve
✓ 90-Day Action Plan: clear steps to build a stronger financial future
{download_text if download_url else ""}
For any questions, please visit: www.nationalbonds.ae

Best regards,
National Bonds Team
"""
    
    def _get_recommended_products(self, survey_response: SurveyResponse, language: str) -> List[Dict[str, str]]:
        """Get recommended products based on financial health score."""
        # Sample products - can be customized based on score ranges
        products_en = [
            {
                'title': 'SAVING BONDS',
                'description': 'A saving plan with a clear path to achieve your goals, and build a better financial future.',
                'image_url': 'https://images.pexels.com/photos/235615/pexels-photo-235615.jpeg?auto=compress&cs=tinysrgb&w=400',
                'link': 'https://nationalbonds.ae/products/saving-bonds'
            },
            {
                'title': 'SECOND SALARY',
                'description': 'Receive a future monthly income with competitive accumulated returns in the UAE.',
                'image_url': 'https://images.pexels.com/photos/1438072/pexels-photo-1438072.jpeg?auto=compress&cs=tinysrgb&w=400',
                'link': 'https://nationalbonds.ae/products/second-salary'
            },
            {
                'title': 'MY MILLION',
                'description': 'The journey to a million is smooth with this plan.',
                'image_url': 'https://images.pexels.com/photos/618613/pexels-photo-618613.jpeg?auto=compress&cs=tinysrgb&w=400',
                'link': 'https://nationalbonds.ae/products/my-million'
            }
        ]
        
        products_ar = [
            {
                'title': 'سندات الادخار',
                'description': 'خطة ادخار مع مسار واضح لتحقيق أهدافك وبناء مستقبل مالي أفضل.',
                'image_url': 'https://images.pexels.com/photos/235615/pexels-photo-235615.jpeg?auto=compress&cs=tinysrgb&w=400',
                'link': 'https://nationalbonds.ae/ar/products/saving-bonds'
            },
            {
                'title': 'الراتب الثاني',
                'description': 'احصل على دخل شهري مستقبلي مع عوائد تراكمية تنافسية في الإمارات.',
                'image_url': 'https://images.pexels.com/photos/1438072/pexels-photo-1438072.jpeg?auto=compress&cs=tinysrgb&w=400',
                'link': 'https://nationalbonds.ae/ar/products/second-salary'
            },
            {
                'title': 'مليوني',
                'description': 'الرحلة إلى المليون سلسة مع هذه الخطة.',
                'image_url': 'https://images.pexels.com/photos/618613/pexels-photo-618613.jpeg?auto=compress&cs=tinysrgb&w=400',
                'link': 'https://nationalbonds.ae/ar/products/my-million'
            }
        ]
        
        return products_ar if language == 'ar' else products_en
    
    def _get_inline_html_template(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str,
        branding_config: Optional[Dict[str, Any]] = None,
        download_url: Optional[str] = None
    ) -> str:
        """Generate inline HTML template for email."""
        # Get branding colors
        primary_color = "#437749"  # Financial Clinic green
        secondary_color = "#3fab4c"  # Button green
        
        if branding_config:
            primary_color = branding_config.get('primary_color', primary_color)
            secondary_color = branding_config.get('secondary_color', secondary_color)
        
        # Generate score summary
        score_summary = self._generate_score_summary_html(survey_response, language)
        
        download_button = f'<div style="text-align: center; margin: 30px 0;"><a href="{download_url or "#"}" style="display: inline-block; background-color: {secondary_color}; color: #ffffff; padding: 16px 40px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">{"تحميل تقرير الصحة المالية" if language == "ar" else "Download My Financial Health Report"}</a></div>'
        
        if language == "ar":
            html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الصحة المالية جاهز</title>
    <style>
        body {{ font-family: 'Poppins', Arial, sans-serif; line-height: 1.6; color: #333; direction: rtl; margin: 0; padding: 0; }}
        .container {{ max-width: 720px; margin: 0 auto; background-color: #ffffff; }}
        .hero {{ background: linear-gradient(to left, rgba(0,0,0,0.5), transparent), url('https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg'); background-size: cover; background-position: center; padding: 60px 40px; text-align: left; }}
        .hero h1 {{ color: #ffffff; font-size: 32px; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
        .content {{ padding: 40px; }}
        .greeting {{ font-size: 16px; font-weight: 600; margin-bottom: 20px; }}
        .paragraph {{ font-size: 16px; margin-bottom: 20px; line-height: 1.6; }}
        .score-box {{ background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%); border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0; }}
        .score-box .score {{ font-size: 72px; font-weight: bold; color: #ffffff; margin: 0; }}
        .score-box .label {{ font-size: 18px; color: #ffffff; margin-top: 10px; }}
        .benefits {{ background-color: #f8fbfd; border: 1px solid #bdcdd6; border-radius: 8px; padding: 24px; margin: 30px 0; }}
        .benefits h3 {{ color: {primary_color}; margin-bottom: 16px; }}
        .benefits ul {{ list-style: none; padding: 0; }}
        .benefits li {{ padding-right: 24px; position: relative; margin-bottom: 12px; color: #767f87; }}
        .benefits li::before {{ content: '✓'; position: absolute; right: 0; color: {secondary_color}; font-weight: bold; }}
        .footer {{ background-color: #f8fbfd; border-top: 1px solid #bdcdd6; padding: 40px; text-align: center; }}
        .footer-text {{ font-size: 11px; color: #a1aeb7; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>تقرير الصحة المالية<br>الخاص بك جاهز!</h1>
        </div>
        <div class="content">
            <p class="greeting">عزيزي {customer_profile.first_name if customer_profile else ""},</p>
            <p class="paragraph">تهانينا، لقد أكملت للتو فحص صحتك المالية!</p>
            <p class="paragraph">تقريرك الشخصي للصحة المالية جاهز، مما يمنحك لمحة واضحة عن وضعك المالي الحالي وخطوات عملية لتعزيزه.</p>
            
            <div class="score-box">
                <div class="score">{int(survey_response.overall_score) if survey_response.overall_score else 0}</div>
                <div class="label">نتيجة الصحة المالية الإجمالية من 100</div>
            </div>
            
            <div class="benefits">
                <h3>داخل تقريرك، ستجد:</h3>
                <ul>
                    <li><strong>نتيجة الصحة المالية:</strong> تفصيل شفاف لأدائك في المجالات الرئيسية</li>
                    <li><strong>توصيات شخصية:</strong> طرق بسيطة وقابلة للتنفيذ لتحسين نتيجتك</li>
                    <li><strong>خطة عمل 90 يوماً:</strong> خطوات واضحة لبناء مستقبل مالي أقوى</li>
                </ul>
            </div>
            
            <p class="paragraph">خذ بضع دقائق لمراجعة نتائجك—إنها الخطوة الأولى نحو مستقبل مالي أقوى وأكثر ثقة.</p>
            
            {download_button}
        </div>
        <div class="footer">
            <p class="footer-text">هذا التقرير لأغراض إعلامية فقط ولا يشكل نصيحة مالية.<br>© {datetime.now().year} السندات الوطنية. جميع الحقوق محفوظة.</p>
        </div>
    </div>
</body>
</html>
"""
        else:
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Financial Health Report is Ready</title>
    <style>
        body {{ font-family: 'Poppins', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
        .container {{ max-width: 720px; margin: 0 auto; background-color: #ffffff; }}
        .hero {{ background: linear-gradient(to right, rgba(0,0,0,0.5), transparent), url('https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg'); background-size: cover; background-position: center; padding: 60px 40px; text-align: right; }}
        .hero h1 {{ color: #ffffff; font-size: 32px; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
        .content {{ padding: 40px; }}
        .greeting {{ font-size: 16px; font-weight: 600; margin-bottom: 20px; }}
        .paragraph {{ font-size: 16px; margin-bottom: 20px; line-height: 1.6; }}
        .score-box {{ background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%); border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0; }}
        .score-box .score {{ font-size: 72px; font-weight: bold; color: #ffffff; margin: 0; }}
        .score-box .label {{ font-size: 18px; color: #ffffff; margin-top: 10px; }}
        .benefits {{ background-color: #f8fbfd; border: 1px solid #bdcdd6; border-radius: 8px; padding: 24px; margin: 30px 0; }}
        .benefits h3 {{ color: {primary_color}; margin-bottom: 16px; }}
        .benefits ul {{ list-style: none; padding: 0; }}
        .benefits li {{ padding-left: 24px; position: relative; margin-bottom: 12px; color: #767f87; }}
        .benefits li::before {{ content: '✓'; position: absolute; left: 0; color: {secondary_color}; font-weight: bold; }}
        .footer {{ background-color: #f8fbfd; border-top: 1px solid #bdcdd6; padding: 40px; text-align: center; }}
        .footer-text {{ font-size: 11px; color: #a1aeb7; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>Your Financial Health<br>Report is Ready!</h1>
        </div>
        <div class="content">
            <p class="greeting">Dear {customer_profile.first_name if customer_profile else "Valued Customer"},</p>
            <p class="paragraph">Congratulations—you've just completed your Financial Checkup!</p>
            <p class="paragraph">Your personalized Financial Health Report is ready, giving you a clear snapshot of your current financial wellbeing and practical steps to strengthen it.</p>
            
            <div class="score-box">
                <div class="score">{int(survey_response.overall_score) if survey_response.overall_score else 0}</div>
                <div class="label">Overall Financial Health Score out of 100</div>
            </div>
            
            <div class="benefits">
                <h3>Inside your report, you'll find:</h3>
                <ul>
                    <li><strong>Your Financial Health Score:</strong> a transparent breakdown of your performance across key areas</li>
                    <li><strong>Personalized Recommendations:</strong> simple, actionable ways to improve your score</li>
                    <li><strong>90-Day Action Plan:</strong> clear steps to build a stronger financial future</li>
                </ul>
            </div>
            
            <p class="paragraph">Take a few minutes to review your results—it's the first step toward a stronger, more confident financial future.</p>
            
            {download_button}
        </div>
        <div class="footer">
            <p class="footer-text">This report is for informational purposes only and does not constitute financial advice.<br>© {datetime.now().year} National Bonds. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content
    
    def _generate_score_summary_html(self, survey_response: SurveyResponse, language: str) -> str:
        """Generate HTML summary of scores by category."""
        categories = [
            ("Budgeting & Income", survey_response.budgeting_score, "إدارة الميزانية والدخل"),
            ("Savings", survey_response.savings_score, "المدخرات"),
            ("Debt Management", survey_response.debt_management_score, "إدارة الديون"),
            ("Financial Planning", survey_response.financial_planning_score, "التخطيط المالي"),
        ]
        
        html = '<div style="margin: 20px 0;"><h3>'
        html += 'تفصيل النتائج:' if language == "ar" else 'Score Breakdown:'
        html += '</h3><ul>'
        
        for category_en, score, category_ar in categories:
            category_name = category_ar if language == "ar" else category_en
            html += f'<li><strong>{category_name}:</strong> {score:.1f}/100</li>'
        
        html += '</ul></div>'
        return html
    
    async def send_reminder_email(
        self,
        recipient_email: str,
        customer_name: str,
        language: str = "en",
        resume_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a reminder email for incomplete assessments."""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            
            # Get frontend URL for logos
            frontend_url = settings.FRONTEND_BASE_URL
            
            if language == "ar":
                msg['Subject'] = "تذكير: أكمل تقييم صحتك المالية"
                content = self._get_reminder_content_ar(customer_name, resume_link)
            else:
                msg['Subject'] = "Reminder: Complete Your Financial Health Assessment"
                content = self._get_reminder_content_en(customer_name, resume_link)
            
            # Replace template placeholders with actual URLs
            content = content.replace('{{frontend_url}}', frontend_url)
            
            msg.attach(MIMEText(content, 'html', 'utf-8'))
            
            delivery_result = self._send_email(msg)
            
            return {
                'success': delivery_result['success'],
                'message': delivery_result['message'],
                'recipient': recipient_email,
                'type': 'reminder'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to send reminder: {str(e)}",
                'recipient': recipient_email,
                'error': str(e)
            }
    
    def _get_reminder_content_en(self, customer_name: str, resume_link: Optional[str] = None) -> str:
        """Get English reminder email content."""
        # Build the continue button HTML
        continue_button = ""
        if resume_link:
            continue_button = f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="{resume_link}" 
                   style="display: inline-block; background-color: #3fab4c; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                    Continue Your Assessment
                </a>
            </div>
            <p style="text-align: center; font-size: 12px; color: #666;">
                Or copy this link: <a href="{resume_link}">{resume_link}</a>
            </p>
            """
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Complete Your Assessment</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header with Logo -->
        <div style="background-color: #437749; padding: 20px; text-align: center;">
            <img src="{{frontend_url}}/homepage/icons/logo.svg" 
                 alt="Financial Clinic" 
                 style="height: 50px; max-width: 200px;">
        </div>
        
        <!-- Main Content -->
        <div style="padding: 30px 20px;">
            <h2 style="color: #437749; margin-top: 0;">Hello {customer_name},</h2>
            
            <p>We noticed you started the Financial Health Assessment but haven't completed it yet.</p>
            
            <p>Your financial wellness is important to us. The assessment takes just 5-10 minutes and provides valuable insights into your financial health.</p>
            
            <p><strong style="color: #437749;">Benefits of completing the assessment:</strong></p>
            <ul style="line-height: 1.8;">
                <li>✓ Personalized financial health score</li>
                <li>✓ Detailed analysis of your financial situation</li>
                <li>✓ Customized recommendations for improvement</li>
                <li>✓ 90-day action plan</li>
            </ul>
            
            {continue_button}
            
            <p>Ready to take control of your financial future?</p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f8f8; padding: 20px; text-align: center; border-top: 1px solid #ddd;">
            <img src="{{frontend_url}}/homepage/images/nbc-logo2-02-1.png" 
                 alt="National Bonds" 
                 style="height: 40px; margin-bottom: 10px;">
            <p style="margin: 5px 0; font-size: 14px; color: #666;">Best regards,<br>National Bonds Team</p>
            <p style="margin: 10px 0; font-size: 12px; color: #999;">
                © {datetime.now().year} National Bonds. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    def _get_reminder_content_ar(self, customer_name: str, resume_link: Optional[str] = None) -> str:
        """Get Arabic reminder email content."""
        # Build the continue button HTML
        continue_button = ""
        if resume_link:
            continue_button = f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="{resume_link}" 
                   style="display: inline-block; background-color: #3fab4c; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                    استمر في التقييم
                </a>
            </div>
            <p style="text-align: center; font-size: 12px; color: #666;">
                أو انسخ هذا الرابط: <a href="{resume_link}">{resume_link}</a>
            </p>
            """
        
        return f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>أكمل تقييمك</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Arial, sans-serif; line-height: 1.6; color: #333; direction: rtl; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header with Logo -->
        <div style="background-color: #437749; padding: 20px; text-align: center;">
            <img src="{{frontend_url}}/homepage/icons/logo.svg" 
                 alt="Financial Clinic" 
                 style="height: 50px; max-width: 200px;">
        </div>
        
        <!-- Main Content -->
        <div style="padding: 30px 20px;">
            <h2 style="color: #437749; margin-top: 0;">مرحباً {customer_name}،</h2>
            
            <p>لاحظنا أنك بدأت تقييم الصحة المالية ولكن لم تكمله بعد.</p>
            
            <p>صحتك المالية مهمة بالنسبة لنا. يستغرق التقييم 5-10 دقائق فقط ويوفر رؤى قيمة حول وضعك المالي.</p>
            
            <p><strong style="color: #437749;">فوائد إكمال التقييم:</strong></p>
            <ul style="line-height: 1.8;">
                <li>✓ نتيجة شخصية للصحة المالية</li>
                <li>✓ تحليل مفصل لوضعك المالي</li>
                <li>✓ توصيات مخصصة للتحسين</li>
                <li>✓ خطة عمل لـ 90 يوماً</li>
            </ul>
            
            {continue_button}
            
            <p>هل أنت مستعد للسيطرة على مستقبلك المالي؟</p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f8f8; padding: 20px; text-align: center; border-top: 1px solid #ddd;">
            <img src="{{frontend_url}}/homepage/images/nbc-logo2-02-1.png" 
                 alt="National Bonds" 
                 style="height: 40px; margin-bottom: 10px;">
            <p style="margin: 5px 0; font-size: 14px; color: #666;">مع أطيب التحيات،<br>فريق السندات الوطنية</p>
            <p style="margin: 10px 0; font-size: 12px; color: #999;">
                © {datetime.now().year} السندات الوطنية. جميع الحقوق محفوظة.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    async def send_financial_clinic_report(
        self,
        recipient_email: str,
        result: Dict[str, Any],
        pdf_content: bytes,
        profile: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Send Financial Clinic assessment report via email.
        
        Args:
            recipient_email: Recipient's email address
            result: Financial Clinic calculation result
            pdf_content: PDF report content as bytes
            profile: Optional user profile information
            language: Language code ('en' or 'ar')
            
        Returns:
            Dictionary with delivery status
        """
        try:
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔍 Email - result type: {type(result)}, profile type: {type(profile)}")
            
            # Ensure profile is None or dict
            if profile is not None and not isinstance(profile, dict):
                logger.warning(f"⚠️ Profile is not a dict! Type: {type(profile)}, Value: {profile}")
                profile = None
            
            # Create email message
            msg = MIMEMultipart('alternative')
            
            # Set email headers
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            
            # Set subject based on language
            if language == "ar":
                msg['Subject'] = "تقرير تقييم العيادة المالية"
            else:
                msg['Subject'] = "Your Financial Clinic Assessment Report"
            
            # Generate email content
            logger.info("📧 Generating HTML content...")
            html_content = self._generate_financial_clinic_email_html(
                result, profile, language
            )
            logger.info("📧 Generating text content...")
            text_content = self._generate_financial_clinic_email_text(
                result, profile, language
            )
            logger.info("📧 Email content generated successfully")
            
            # Attach HTML and text versions
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # Attach PDF report
            pdf_attachment = MIMEBase('application', 'pdf')
            pdf_attachment.set_payload(pdf_content)
            encoders.encode_base64(pdf_attachment)
            
            filename = f"financial_clinic_report_{datetime.now().strftime('%Y%m%d')}.pdf"
            pdf_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{filename}"'
            )
            msg.attach(pdf_attachment)
            
            # Send email
            delivery_result = self._send_email(msg)
            
            return {
                'success': delivery_result['success'],
                'message': delivery_result['message'],
                'recipient': recipient_email,
                'subject': msg['Subject'],
                'attachment_size': len(pdf_content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to send email: {str(e)}",
                'recipient': recipient_email,
                'error': str(e)
            }
    
    def _generate_financial_clinic_email_html(
        self,
        result: Dict[str, Any],
        profile: Optional[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate HTML email content for Financial Clinic report - Updated to match new design."""
        # Handle case where result might be a string (shouldn't happen but defensive programming)
        if isinstance(result, str):
            import json
            try:
                result = json.loads(result)
            except:
                result = {}
        
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            result = {}
        
        # Use total_score from Financial Clinic (not overall_score)
        score = result.get('total_score', result.get('overall_score', 0))
        categories = result.get('category_scores', [])
        insights = result.get('insights', [])
        
        # Updated colors to match new design
        primary_color = "#2e9e42"  # Main green
        score_color = "#2e9e42"  # Consistent green for score
        gradient_start = "#57b957"
        gradient_end = "#2e9e42"
        
        # Get user name
        user_name = profile.get('name', '') if profile else ''
        
        # Build category HTML for Arabic
        categories_html_ar = ""
        for cat in categories:
            # Defensive: ensure cat is a dict
            if not isinstance(cat, dict):
                continue
            cat_name_ar = cat.get('category_ar', cat.get('category', ''))
            cat_score = cat.get('score', 0)
            cat_color = self._get_category_color(cat.get('status_level', 'moderate'))
            categories_html_ar += f"""
                <div class="category">
                    <span class="category-name">{cat_name_ar}</span>
                    <span class="category-score" style="color: {cat_color};">{cat_score:.1f}</span>
                    <div style="clear: both;"></div>
                </div>
            """
        
        # Build category HTML for English
        categories_html_en = ""
        for cat in categories:
            # Defensive: ensure cat is a dict
            if not isinstance(cat, dict):
                continue
            cat_name = cat.get('category', '')
            cat_score = cat.get('score', 0)
            cat_color = self._get_category_color(cat.get('status_level', 'moderate'))
            categories_html_en += f"""
                <div class="category">
                    <span class="category-name">{cat_name}</span>
                    <span class="category-score" style="color: {cat_color};">{cat_score:.1f}</span>
                </div>
            """
        
        # Get user name safely (avoid None.get() error)
        user_name = profile.get('name', '') if profile else ''
        
        # Build insights HTML
        insights_html_ar = ""
        insights_html_en = ""
        for idx, insight in enumerate(insights[:5], 1):
            if isinstance(insight, dict):
                category = insight.get('category', '')
                text = insight.get('text', str(insight))
                insights_html_ar += f"<li><strong>{idx}. {category}:</strong> {text}</li>"
                insights_html_en += f"<li><strong>{idx}. {category}:</strong> {text}</li>"
            else:
                insights_html_ar += f"<li>{idx}. {str(insight)}</li>"
                insights_html_en += f"<li>{idx}. {str(insight)}</li>"
        
        if language == "ar":
            return f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير العيادة المالية</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; direction: rtl; background: white; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: white; }}
        .header {{ background-color: white; padding: 30px 20px; text-align: center; }}
        .header h1 {{ color: #374151; font-size: 28px; margin: 0 0 10px 0; }}
        .header p {{ color: #9ca3af; font-size: 14px; margin: 5px 0; }}
        .score-display {{ text-align: center; padding: 30px 0; }}
        .score {{ font-size: 72px; font-weight: bold; color: {score_color}; margin: 20px 0; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e5e7eb; border-radius: 10px; overflow: hidden; margin: 20px 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(to right, {gradient_start}, {gradient_end}); border-radius: 10px; }}
        .content {{ padding: 20px; background: white; }}
        .section-title {{ font-size: 24px; font-weight: bold; color: #374151; text-align: center; margin: 30px 0 15px 0; }}
        .section-subtitle {{ font-size: 14px; color: #9ca3af; text-align: center; margin-bottom: 20px; }}
        .category {{ display: flex; justify-content: space-between; align-items: center; padding: 12px; margin: 10px 0; border-bottom: 1px solid #e5e7eb; }}
        .category-name {{ font-weight: 600; color: #374151; }}
        .category-score {{ font-size: 16px; color: #6b7280; }}
        .action-plan-box {{ background: #f9fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .action-plan-box ul {{ list-style: none; padding: 0; margin: 15px 0 0 0; }}
        .action-plan-box li {{ padding: 10px 0; border-right: 3px solid {primary_color}; padding-right: 12px; margin-bottom: 10px; color: #374151; }}
        .score-bands {{ display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }}
        .band {{ flex: 1; min-width: 120px; padding: 15px; border-radius: 8px; text-align: center; color: white; }}
        .band-red {{ background: #ee3b37; }}
        .band-orange {{ background: #fead2a; }}
        .band-yellow {{ background: #e7e229; color: #374151; }}
        .band-green {{ background: #57b957; }}
        .band-range {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
        .band-label {{ font-size: 13px; font-weight: 600; margin-bottom: 5px; }}
        .band-desc {{ font-size: 11px; opacity: 0.9; }}
        .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; font-size: 14px; border-radius: 8px; margin-top: 30px; }}
        .cta-button {{ display: inline-block; background: {primary_color}; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>إليك درجة صحتك المالية!</h1>
            <p>هذه لمحة سريعة، نظرة واضحة على مدى صحة أموالك اليوم</p>
        </div>
        
        <div class="score-display">
            <div class="score">{round(score)}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {score}%;"></div>
            </div>
        </div>
        
        <div class="content">
            <div class="section-title">فهم نتيجتك</div>
            <div class="score-bands">
                <div class="band band-red">
                    <div class="band-range">1-29</div>
                    <div class="band-label">في خطر</div>
                    <div class="band-desc">ركز على بناء عادات مالية أساسية</div>
                </div>
                <div class="band band-orange">
                    <div class="band-range">30-59</div>
                    <div class="band-label">يحتاج إلى تحسين</div>
                    <div class="band-desc">أساس جيد، مجال للنمو</div>
                </div>
                <div class="band band-yellow">
                    <div class="band-range">60-79</div>
                    <div class="band-label">جيد</div>
                    <div class="band-desc">صحة مالية قوية</div>
                </div>
                <div class="band band-green">
                    <div class="band-range">80-100</div>
                    <div class="band-label">ممتاز</div>
                    <div class="band-desc">رفاهية مالية متميزة</div>
                </div>
            </div>
            
            <div class="section-title">درجات الركائز المالية</div>
            <div class="section-subtitle">أدائك عبر 7 مجالات رئيسية للصحة المالية</div>
            {categories_html_ar}
            
            <div class="section-title">خطة عملك الشخصية</div>
            <div class="section-subtitle">التغييرات الصغيرة تحدث فرقًا كبيرًا. إليك كيفية تقوية نتيجتك</div>
            <div class="action-plan-box">
                <div style="font-weight: 600; margin-bottom: 10px;">فئات التوصيات:</div>
                <ul>{insights_html_ar}</ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://www.nationalbonds.ae/ar/contact-us" class="cta-button">احجز استشارة مجانية</a>
                <a href="https://nationalbonds.onelink.me/NAu3/9m8huddj" class="cta-button">ابدأ الادخار مع السندات الوطنية</a>
            </div>
            
            <p style="text-align: center; color: #6b7280;"><strong>تذكر:</strong> تحسين صحتك المالية رحلة تتطلب الصبر والمثابرة. نحن معك في كل خطوة!</p>
        </div>
        
        <div class="footer">
            <p style="margin: 5px 0; color: #6b7280;">هذا التقرير لأغراض إعلامية فقط</p>
            <p style="margin: 5px 0; font-weight: bold; color: #374151;">السندات الوطنية</p>
            <p style="margin: 5px 0; color: #6b7280;">www.nationalbonds.ae</p>
        </div>
    </div>
</body>
</html>
"""
        else:
            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Clinic Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: white; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: white; }}
        .header {{ background-color: white; padding: 30px 20px; text-align: center; }}
        .header h1 {{ color: #374151; font-size: 28px; margin: 0 0 10px 0; }}
        .header p {{ color: #9ca3af; font-size: 14px; margin: 5px 0; }}
        .score-display {{ text-align: center; padding: 30px 0; }}
        .score {{ font-size: 72px; font-weight: bold; color: {score_color}; margin: 20px 0; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e5e7eb; border-radius: 10px; overflow: hidden; margin: 20px 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(to right, {gradient_start}, {gradient_end}); border-radius: 10px; }}
        .content {{ padding: 20px; background: white; }}
        .section-title {{ font-size: 24px; font-weight: bold; color: #374151; text-align: center; margin: 30px 0 15px 0; }}
        .section-subtitle {{ font-size: 14px; color: #9ca3af; text-align: center; margin-bottom: 20px; }}
        .category {{ display: flex; justify-content: space-between; align-items: center; padding: 12px; margin: 10px 0; border-bottom: 1px solid #e5e7eb; }}
        .category-name {{ font-weight: 600; color: #374151; }}
        .category-score {{ font-size: 16px; color: #6b7280; }}
        .action-plan-box {{ background: #f9fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .action-plan-box ul {{ list-style: none; padding: 0; margin: 15px 0 0 0; }}
        .action-plan-box li {{ padding: 10px 0; border-left: 3px solid {primary_color}; padding-left: 12px; margin-bottom: 10px; color: #374151; }}
        .score-bands {{ display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }}
        .band {{ flex: 1; min-width: 120px; padding: 15px; border-radius: 8px; text-align: center; color: white; }}
        .band-red {{ background: #ee3b37; }}
        .band-orange {{ background: #fead2a; }}
        .band-yellow {{ background: #e7e229; color: #374151; }}
        .band-green {{ background: #57b957; }}
        .band-range {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
        .band-label {{ font-size: 13px; font-weight: 600; margin-bottom: 5px; }}
        .band-desc {{ font-size: 11px; opacity: 0.9; }}
        .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; font-size: 14px; border-radius: 8px; margin-top: 30px; }}
        .cta-button {{ display: inline-block; background: {primary_color}; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Here's your Financial Health Score!</h1>
            <p>This is your snapshot, a clear view of how healthy your finances are today.</p>
        </div>
        
        <div class="score-display">
            <div class="score">{round(score)}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {score}%;"></div>
            </div>
        </div>
        
        <div class="content">
            <div class="section-title">Understanding Your Score</div>
            <div class="score-bands">
                <div class="band band-red">
                    <div class="band-range">1-29</div>
                    <div class="band-label">At Risk</div>
                    <div class="band-desc">Focus on building basic financial habits</div>
                </div>
                <div class="band band-orange">
                    <div class="band-range">30-59</div>
                    <div class="band-label">Needs Improvement</div>
                    <div class="band-desc">Good foundation, room for growth</div>
                </div>
                <div class="band band-yellow">
                    <div class="band-range">60-79</div>
                    <div class="band-label">Good</div>
                    <div class="band-desc">Strong financial health</div>
                </div>
                <div class="band band-green">
                    <div class="band-range">80-100</div>
                    <div class="band-label">Excellent</div>
                    <div class="band-desc">Outstanding financial wellness</div>
                </div>
            </div>
            
            <div class="section-title">Financial Pillar Scores</div>
            <div class="section-subtitle">Your performance across the 7 key areas of financial health</div>
            {categories_html_en}
            
            <div class="section-title">Your Personalized Action Plan</div>
            <div class="section-subtitle">Small changes make big differences. Here's how to strengthen your score.</div>
            <div class="action-plan-box">
                <div style="font-weight: 600; margin-bottom: 10px;">Recommendation Categories:</div>
                <ul>{insights_html_en}</ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://www.nationalbonds.ae/en/contact-us" class="cta-button">BOOK A FREE CONSULTATION</a>
                <a href="https://nationalbonds.onelink.me/NAu3/9m8huddj" class="cta-button">START SAVING WITH NATIONAL BONDS</a>
            </div>
            
            <p style="text-align: center; color: #6b7280;"><strong>Remember:</strong> Improving your financial health is a journey that requires patience and persistence. We're with you every step of the way!</p>
        </div>
        
        <div class="footer">
            <p style="margin: 5px 0; color: #6b7280;">This report is for informational purposes only</p>
            <p style="margin: 5px 0; font-weight: bold; color: #374151;">National Bonds</p>
            <p style="margin: 5px 0; color: #6b7280;">www.nationalbonds.ae</p>
        </div>
    </div>
</body>
</html>
"""
    
    def _generate_financial_clinic_email_text(
        self,
        result: Dict[str, Any],
        profile: Optional[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate plain text email content for Financial Clinic report."""
        score = result.get('total_score', result.get('overall_score', 0))
        user_name = profile.get('name', '') if profile else ''
        
        if language == "ar":
            return f"""
مرحباً {user_name},

شكراً لك على إكمال تقييم العيادة المالية!

نتيجتك الإجمالية: {score:.1f}/100

تجد مرفقاً تقريراً مفصلاً يتضمن:
• تحليل تفصيلي لجميع جوانب صحتك المالية
• توصيات شخصية مبنية على إجاباتك
• خطوات عملية لتحسين وضعك المالي
• موارد تعليمية مفيدة

الخطوات التالية:
1. راجع التقرير المفصل المرفق بعناية
2. حدد أولوياتك المالية
3. ابدأ بتطبيق التوصيات الأكثر تأثيراً

للاستفسارات: www.nationalbonds.ae

مع أطيب التحيات,
فريق السندات الوطنية
"""
        else:
            return f"""
Hello {user_name},

Thank you for completing the Financial Clinic assessment!

Your Overall Score: {score:.1f}/100

Please find attached your detailed report including:
• Comprehensive analysis of all aspects of your financial health
• Personalized recommendations based on your responses
• Actionable steps to improve your financial situation
• Helpful educational resources

Next Steps:
1. Review your detailed report attached carefully
2. Identify your financial priorities
3. Start implementing the most impactful recommendations

"""
    
    def _get_category_color(self, status_level: str) -> str:
        """Get color code based on status level."""
        color_map = {
            'excellent': '#059669',  # Green
            'good': '#3b82f6',       # Blue
            'moderate': '#f59e0b',   # Amber
            'needs_attention': '#ef4444',  # Red
            'at_risk': '#991b1b'     # Dark Red
        }
        return color_map.get(status_level.lower(), '#6b7280')  # Gray as default
    
    async def send_otp_email(
        self,
        recipient_email: str,
        otp_code: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Send OTP verification code via email.
        
        Args:
            recipient_email: Recipient's email address
            otp_code: 6-digit OTP code
            language: Email language ('en' or 'ar')
            
        Returns:
            Dict with success status and message
        """
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            
            # Set email headers
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            
            # Set subject based on language
            if language == "ar":
                msg['Subject'] = "رمز التحقق الخاص بك - صكوك الوطنية"
            else:
                msg['Subject'] = "Your Verification Code - National Bonds"
            
            # Load and render template
            if self.jinja_env:
                try:
                    template = self.jinja_env.get_template(f'otp_email_{language}.html')
                    html_content = template.render(otp_code=otp_code)
                except Exception as e:
                    # Fallback to simple HTML if template not found
                    html_content = self._generate_simple_otp_html(otp_code, language)
            else:
                html_content = self._generate_simple_otp_html(otp_code, language)
            
            # Create plain text version
            if language == "ar":
                text_content = f"""
صكوك الوطنية - فحص الصحة المالية

رمز التحقق الخاص بك: {otp_code}

ينتهي هذا الرمز خلال 5 دقائق.
لا تشارك هذا الرمز مع أي شخص.

إذا لم تطلب هذا الرمز، يرجى تجاهل هذا البريد الإلكتروني.
"""
            else:
                text_content = f"""
National Bonds - Financial Health Check

Your Verification Code: {otp_code}

This code expires in 5 minutes.
Never share this code with anyone.

If you didn't request this code, please ignore this email.
"""
            
            # Attach both versions
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # Send email
            delivery_result = self._send_email(msg)
            
            return {
                'success': delivery_result['success'],
                'message': 'OTP sent successfully' if delivery_result['success'] else 'Failed to send OTP',
                'recipient': recipient_email,
                'code_length': len(otp_code)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to send OTP email: {str(e)}",
                'recipient': recipient_email,
                'error': str(e)
            }
    
    def _generate_simple_otp_html(self, otp_code: str, language: str) -> str:
        """Generate simple OTP HTML email when template is not available."""
        # Get frontend URL for logos
        frontend_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        
        if language == "ar":
            return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رمز التحقق</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Arial, sans-serif; line-height: 1.6; color: #333; direction: rtl; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header with Logo -->
        <div style="background-color: #437749; padding: 20px; text-align: center;">
            <img src="{frontend_url}/homepage/icons/logo.svg" 
                 alt="Financial Clinic" 
                 style="height: 50px; max-width: 200px;">
        </div>
        
        <!-- Main Content -->
        <div style="padding: 30px 20px; text-align: center;">
            <h2 style="color: #437749; margin-bottom: 20px;">رمز التحقق الخاص بك</h2>
            
            <div style="background: #f8fbfd; padding: 30px; text-align: center; border: 2px solid #437749; border-radius: 12px; margin: 20px 0;">
                <div style="font-size: 42px; font-weight: bold; letter-spacing: 8px; color: #437749; margin: 10px 0;">
                    {otp_code}
                </div>
            </div>
            
            <p style="color: #dc3545; margin: 15px 0; font-weight: 600;">ينتهي خلال 5 دقائق</p>
            <p style="color: #666; margin: 20px 0;">لا تشارك هذا الرمز مع أي شخص.</p>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #856404; font-size: 14px;">
                    إذا لم تطلب هذا الرمز، يرجى تجاهل هذا البريد الإلكتروني.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f8f8; padding: 20px; text-align: center; border-top: 1px solid #ddd;">
            <img src="{frontend_url}/homepage/images/nbc-logo2-02-1.png" 
                 alt="National Bonds" 
                 style="height: 40px; margin-bottom: 10px;">
            <p style="margin: 5px 0; font-size: 14px; color: #666;">مع أطيب التحيات،<br>فريق السندات الوطنية</p>
            <p style="margin: 10px 0; font-size: 12px; color: #999;">
                © {datetime.now().year} السندات الوطنية. جميع الحقوق محفوظة.
            </p>
        </div>
    </div>
</body>
</html>
"""
        else:
            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Code</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header with Logo -->
        <div style="background-color: #437749; padding: 20px; text-align: center;">
            <img src="{frontend_url}/homepage/icons/logo.svg" 
                 alt="Financial Clinic" 
                 style="height: 50px; max-width: 200px;">
        </div>
        
        <!-- Main Content -->
        <div style="padding: 30px 20px; text-align: center;">
            <h2 style="color: #437749; margin-bottom: 20px;">Your Verification Code</h2>
            
            <div style="background: #f8fbfd; padding: 30px; text-align: center; border: 2px solid #437749; border-radius: 12px; margin: 20px 0;">
                <div style="font-size: 42px; font-weight: bold; letter-spacing: 8px; color: #437749; margin: 10px 0;">
                    {otp_code}
                </div>
            </div>
            
            <p style="color: #dc3545; margin: 15px 0; font-weight: 600;">Expires in 5 minutes</p>
            <p style="color: #666; margin: 20px 0;">Never share this code with anyone.</p>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #856404; font-size: 14px;">
                    If you didn't request this code, please ignore this email.
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f8f8; padding: 20px; text-align: center; border-top: 1px solid #ddd;">
            <img src="{frontend_url}/homepage/images/nbc-logo2-02-1.png" 
                 alt="National Bonds" 
                 style="height: 40px; margin-bottom: 10px;">
            <p style="margin: 5px 0; font-size: 14px; color: #666;">Best regards,<br>National Bonds Team</p>
            <p style="margin: 10px 0; font-size: 12px; color: #999;">
                © {datetime.now().year} National Bonds. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""