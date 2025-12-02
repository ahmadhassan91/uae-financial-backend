"""Email service for delivering financial health reports."""
import os
import smtplib
import json
import logging
import unicodedata
import hashlib
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
        """Send email using SMTP - exact production approach."""
        try:
            # Extract recipient email address (remove any formatting)
            to_email = msg['To']
            if '<' in to_email and '>' in to_email:
                # Extract email from "Name <email@domain.com>" format
                to_email = to_email.split('<')[1].split('>')[0].strip()
            
            # Use exact working approach
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('ahmad.hassan@clustox.com', 'uvrf ptoj dogy xzne')
            
            # Use as_string() exactly like the working test
            msg_string = msg.as_string()
            server.sendmail('ahmad.hassan@clustox.com', [to_email], msg_string)
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
        base_url = settings.base_url
        
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
        'description': 'Our Saving bonds empower you to achieve your goals, and build a secure safety net, on your terms. ',
        'image_tag': '<img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/Coins_btvqsu.png" alt="Saving Bonds" />',
        'link': 'https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/Coins_btvqsu.png'
    },
    {
        'title': 'SECOND SALARY',
        'description': 'Receive a future monthly income with competitive accumulated returns in the UAE.',
        'image_tag': '<img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/Second_Salary_vxewl3.png" alt="Second Salary" />',
        'link': 'https://nationalbonds.ae/products/second-salary'
    },
    {
        'title': 'MY MILLION',
        'description': 'The journey to a million is smooth with this plan.',
        'image_tag': '<img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/My_Million_hsata5.png" alt="My Million" />',
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
        .footer {{ background-color: #f8fbfd; border-top: 1px solid #bdcdd6; text-align: center; }}
        .footer-text {{ font-size: 11px; color: #a1aeb7;}}
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
            frontend_url = settings.base_url
            
            if language == "ar":
                msg['Subject'] = "تذكير: أكمل تقييم صحتك المالية"
                content = self._get_reminder_content_ar(customer_name, resume_link)
            else:
                msg['Subject'] = "Reminder: Complete Your Financial Health Assessment"
                content = self._get_reminder_content_en(customer_name, resume_link)
            
            # Replace template placeholders with actual URLs
            content = content.replace('{}', frontend_url)
            
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
            <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332361/financial_clinic_nep6cd.png" 
                 alt="Financial Clinic" 
                 style="height: 30px; max-width: 200px;">
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
            <img src=" https://res.cloudinary.com/dhujwbcor/image/upload/v1764334328/logo_bhsixi.png" 
                 alt="National Bonds" 
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
            <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332361/financial_clinic_nep6cd.png" 
                 alt="Financial Clinic" 
                 style="height: 30px; max-width: 200px;">
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
            <img src=" https://res.cloudinary.com/dhujwbcor/image/upload/v1764334328/logo_bhsixi.png" 
                 alt="National Bonds" 
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
        language: str = "en",
        download_url: Optional[str] = None
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
            
            # Store PDF for download if not provided with download_url
            if download_url is None and pdf_content:
                logger.info("💾 Storing PDF for download...")
                # Generate unique identifier
                recipient_hash = hashlib.md5(recipient_email.encode()).hexdigest()[:8]
                download_url = self._store_pdf_for_download(pdf_content, recipient_hash)
                logger.info(f"✅ PDF stored with download URL: {download_url}")
            
            # Generate email content
            logger.info("📧 Generating HTML content...")
            html_content = self._generate_financial_clinic_email_html(
                result, profile, language, download_url
            )
            logger.info("📧 Generating text content...")
            text_content = self._generate_financial_clinic_email_text(
                result, profile, language
            )
            logger.info("📧 Email content generated successfully")
            
            # Attach HTML and text versions
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
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
        language: str,
        download_url: Optional[str] = None
    ) -> str:
        """Generate HTML email content for Financial Clinic report - Updated to match new design."""
        # Get frontend URL for images
        frontend_url = settings.base_url
        
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
            <img src="/homepage/icons/image3.png" alt="Financial Health" style="max-width: 100px; height: auto; margin-bottom: 20px;" />
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
                <div style="margin-bottom: 20px;">
                    {f'<a href="{download_url}" class="cta-button" style="background: #1f2937; margin: 5px; text-decoration: none;" download="financial_clinic_report.pdf">📄 تحميل التقرير المفصل</a>' if download_url else '<a href="#attachment" class="cta-button" style="background: #1f2937; margin: 5px; cursor: pointer;" title="تحقق من مرفقات بريدك الإلكتروني لتحميل تقرير PDF">📄 تحميل التقرير المفصل</a>'}
                    {'' if download_url else '<p style="font-size: 12px; color: #6b7280; margin-top: 10px;">📎 تقريرك المفصل بصيغة PDF مرفق بهذا البريد الإلكتروني. يرجى التحقق من مرفقات بريدك الإلكتروني لتحميله.</p>'}
                </div>
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
        .container {{ max-width: 945px; margin: 0 auto; padding: 20px; background: white; }}
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
            <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332338/Man_qt2i81.png" alt="Financial Health" style="width:788px; height: 499px; margin-bottom: 20px;" />
            
        </div>
        <div>
            <span style="font-size:18px; font-weight:700; color:#3D4D57;font-size:16px; font-weight:600; color:#3D4D57;">Dear {profile.get('name', 'Valued Customer') if profile else 'Valued Customer'}</span>
        </div>
        <div style="margin-top:18px;">
            <span style="font-size:20px; font-weight:600; color:#3D4D57; display:block; margin-bottom:8px;">Congratulations you’ve just completed your Financial Checkup!</span>
            <span style="font-size:16px; color:#3D4D57; font-weight:600;display:block; margin-bottom:8px;">Your personalized Financial Health Report is ready, giving you a clear snapshot of your current financial wellbeing and practical steps to strengthen it.</span>
            <span style="font-size:16px; color:#3D4D57; display:block;font-weight:600; margin-bottom:8px;">Inside your report, you’ll find:</span>
        </div>
        <div style="margin:32px 0 24px 0; text-align:left;">
            <span style="font-size:16px; font-weight:700; color:#3D4D57;">Your Financial Health Score:</span>
            <span style="font-size:16px; color:#3D4D57; display:block; margin-top:8px;">a transparent breakdown of how you’re doing across key areas like savings, income, debt, and protection.</span>
        </div>
        <div style="margin:32px 0 24px 0; text-align:left;">
            <span style="font-size:16px; font-weight:700; color:#3D4D57;">Personalized Recommendations:</span>
            <span style="font-size:16px; color:#3D4D57; display:block; margin-top:8px;">simple, actionable ways to improve your score and achieve your goals.</span>
        </div>
        <div style="margin:32px 0 24px 0; text-align:left;">
            <span style="font-size:16px; color:#3D4D57; display:block; margin-top:8px;">Take a few minutes to review your results, it’s the first step toward a stronger, more confident financial future.</span>
        </div>
        <div style="text-align: center; margin: 30px 0;">
            <div style="margin-bottom: 20px; "font-size:16px; font-weight:600; color:#3D4D57;">
                {f'<a href="{download_url}" class="cta-button" style="background: #3FAB4C; margin: 5px; text-decoration: none; color:white; font-weight:600;" download="financial_clinic_report.pdf">DOWNLOAD MY FINANCIAL HEALTH REPORT</a>' if download_url else '<a href="#attachment" class="cta-button" style="background: #1f2937; margin: 5px; cursor: pointer; color:#1A237E; font-weight:600;" title="Check your email attachments to download the PDF report">📄 DOWNLOAD MY FINANCIAL HEALTH REPORT</a>'}
                {'' if download_url else '<p style="font-size: 12px; color: #6b7280; margin-top: 10px;">📎 Your detailed PDF report is attached to this email. Please check your email attachments to download it.</p>'}
            </div>
            
        </div>
        <div>
          <span style="text-align:left; font-size:16px; font-weight:600; color:#3D4D57;">Your Personalized Financial Path</span>
            </div>
            <div>
            <span style="font-size:16px; font-weight:600; color:#3D4D57;">Based on your score, we’ve selected products tailored to your goals and current financial stage:</span>
            </div>
            <div>
         
        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0 40px 0;">
            <tr>
                <td style="width:30%; padding:10px; vertical-align:top;">
                    <div style="border:1px solid #e5e7eb; border-radius:12px; overflow:hidden; background:#fff;">
                    <div style="padding:18px 16px 0 16px;">
                            <div style="font-size:16px; font-weight:700; color:#374151; text-align:center; margin-bottom:8px;">SAVING BONDS</div>
                            <div style="font-size:14px; color:#374151; text-align:center; margin-bottom:12px;">Our Saving bonds empower you to achieve your goals, and build a secure safety net, on your terms. </div>
                        </div>
                        <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/Coins_btvqsu.png" alt="Saving Bonds" style="width:100%; width: 285px;
    height: 185px;object-fit:cover; border-bottom:1px solid #e5e7eb;" />
                        
                        <a href="https://nationalbonds.ae/products/saving-bonds" style="display:block; background:#374151; color:#fff; text-align:center; padding:14px 0; font-weight:600; text-decoration:none; font-size:15px;">KNOW MORE</a>
                    </div>
                </td>
                <td style="width:30%; padding:10px; vertical-align:top;">
                    <div style="border:1px solid #e5e7eb; border-radius:12px; overflow:hidden; background:#fff;">
                     <div style="padding:18px 16px 0 16px;">
                            <div style="font-size:16px; font-weight:700; color:#374151; text-align:center; margin-bottom:8px;">SECOND SALARY</div>
                            <div style="font-size:14px; color:#374151; text-align:center; margin-bottom:12px;">Receive a future monthly income with competitive anticipated returns included.</div>
                        </div>
                        <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/Second_Salary_vxewl3.png" alt="Second Salary" style="width:100%; width: 285px;
    height: 185px; object-fit:cover; border-bottom:1px solid #e5e7eb;" />

                        <a href="https://nationalbonds.ae/products/second-salary" style="display:block; background:#374151; color:#fff; text-align:center; padding:14px 0; font-weight:600; text-decoration:none; font-size:15px;">KNOW MORE</a>
                    </div>
                </td>
                <td style="width:30%; padding:10px; vertical-align:top;">
                    <div style="border:1px solid #e5e7eb; border-radius:12px; overflow:hidden; background:#fff;">
                     <div style="padding:18px 16px 0 16px;">
                            <div style="font-size:16px; font-weight:700; color:#374151; text-align:center; margin-bottom:8px;">MY MILLIONS</div>
                            <div style="font-size:14px; color:#374151; text-align:center; margin-bottom:12px;">The journey to a million is smooth with this plan.</div>
                        </div>
                        <img src=" https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/My_Million_hsata5.png" alt="My Millions" style="width:100%; width: 285px;
    height: 185px; object-fit:cover; border-bottom:1px solid #e5e7eb;" />

                        <a href="https://nationalbonds.ae/products/my-millions" style="display:block; background:#374151; color:#fff; text-align:center; padding:14px 0; font-weight:600; text-decoration:none; font-size:15px;">KNOW MORE</a>
                    </div>
                </td>
            </tr>
        </table>
<div style="display: flex;
    width: 100%;
    justify-content: center">
 <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332361/financial_clinic_nep6cd.png" alt="National Bonds" style="height:48px; margin-left:45%;" />
</div>

                <table class="footer" width="100%" cellpadding="0" cellspacing="0" style="background:#fff; border-top:1px solid #e5e7eb;">
                    <tr>
                        <!-- Logo Left -->
                        <td align="left" style="vertical-align:middle;">
                            <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764334328/logo_bhsixi.png" alt="National Bonds" style="height:200px; width:250px;margin-right:12px;" />
                        </td>
                        <!-- Social Icons Center -->
                        <td align="center" style="vertical-align:middle;padding-right:80px;">
                            <table cellpadding="0" cellspacing="0" style="margin-bottom:8px;"><tr>
                                <td style="padding:0 9px;">
                                    <a href="https://www.facebook.com/nationalbonds">
                                        <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332010/grommet-icons_facebook-option_ukdarn.png" alt="Facebook" style="width:30px; height:30px; border-radius:50%; border:2px solid #b8985f; display:inline-block; padding:4px; box-sizing:border-box;" />
                                    </a>
                                </td>
                                <td style="padding:0 9px;">
                                    <a href="https://www.instagram.com/nationalbonds/">
                                        <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764333399/instagram_khxfre.png" alt="Instagram" style="width:30px; height:30px; border-radius:50%; border:2px solid #b8985f; display:inline-block; padding:4px; box-sizing:border-box;" />
                                    </a>
                                </td>
                                <td style="padding:0 9px;">
                                    <a href="https://www.linkedin.com/company/national-bonds-corporation">
                                        <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764333370/linkedin_uxkfhj.png" alt="LinkedIn" style="width:30px; height:30px; border-radius:50%; border:2px solid #b8985f; display:inline-block; padding:4px; box-sizing:border-box;" />
                                    </a>
                                </td>
                                <td style="padding:0 9px;">
                                    <a href="https://www.youtube.com/user/NationalBondsDubai/videos">
                                        <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/youtube_ftgawy.png" alt="YouTube" style="width:30px; height:30px; border-radius:50%; border:2px solid #b8985f; display:inline-block; padding:4px; box-sizing:border-box;" />
                                    </a>
                                </td>
                            </tr></table>
                            <div style="font-size:10px; color:#6b7280;">STAY CONNECTED</div>
                        </td>
                        <!-- App/Branches Right -->
                        <td align="center" style="vertical-align:middle; padding-right:30px;">
                            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
                                <tr>
                                    <td style="padding:0 18px; text-align:center; vertical-align:top;">
                                       <span style="display:inline-block; width:32px;margin-bottom: 10px; height:32px; border-radius:50%; border:2px solid #b8985f; background:#fff; display:flex; align-items:center; justify-content:center; padding:4px; box-sizing:border-box;">
  <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/downlaod_tzobjf.png" alt="Download App" style="width:18px; height:18px; display:block;" />
</span>
                                        <div style="font-size:10px; color:#6b7280;">DOWNLOAD OUR APP</div>
                                    </td>
                                    <td style="padding:0 18px; text-align:center; vertical-align:top;">
                                       <span style="display:inline-block; width:32px; margin-bottom: 10px;height:32px; border-radius:50%; border:2px solid #b8985f; background:#fff; display:flex; align-items:center; justify-content:center; padding:4px; box-sizing:border-box;">
  <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/location_bmwxm8.png" alt="Branches" style="width:18px; height:18px; display:block;" />
</span>
                                        <div style="font-size:10px; color:#6b7280;">OUR BRANCHES</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
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
    
    def _store_pdf_for_download(self, pdf_content: bytes, identifier: str) -> str:
        """Store PDF file (S3 or local) and return download URL."""
        import os
        import hashlib
        from datetime import datetime
        from app.reports.s3_storage import s3_storage
        
        # Generate unique token for file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        token = hashlib.md5(f"{identifier}_{timestamp}".encode()).hexdigest()[:12]
        filename = f"{token}_financial_clinic_report.pdf"
        
        # Try S3 storage first
        if settings.USE_S3_STORAGE:
            try:
                # Upload to S3 with reports/ prefix
                s3_key = f"reports/{filename}"
                s3_url = s3_storage.upload_pdf(
                    pdf_content=pdf_content,
                    file_key=s3_key,
                    metadata={
                        'identifier': identifier,
                        'timestamp': timestamp,
                        'type': 'financial_clinic_report'
                    }
                )
                
                if s3_url:
                    logging.info(f"✅ PDF stored in S3: {s3_url}")
                    return s3_url
                else:
                    logging.warning("⚠️ S3 upload failed, falling back to local storage")
            except Exception as e:
                logging.error(f"❌ S3 storage error: {e}, falling back to local storage")
        
        # Fallback to local storage
        downloads_dir = settings.DOWNLOAD_DIR
        os.makedirs(downloads_dir, exist_ok=True)
        
        file_path = os.path.join(downloads_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(pdf_content)
        
        # Generate download URL for local storage
        base_url = settings.api_base_url
        download_url = f"{base_url}/api/v1/reports/download-public/{token}"
        
        logging.info(f"📁 PDF stored locally: {download_url}")
        return download_url
    
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
            # Create email message (use simple approach for OTP)
            msg = MIMEMultipart('alternative')
            
            # Clean all text inputs to avoid Unicode issues
            import unicodedata
            from datetime import datetime
            
            def clean_text(text):
                text = unicodedata.normalize('NFKC', text)
                text = text.replace('\xa0', ' ')  # non-breaking space
                text = text.replace('\u2019', "'")  # smart quote
                text = text.replace('\u2018', "'")  # smart quote
                text = text.replace('\u201c', '"')  # smart quote
                text = text.replace('\u201d', '"')  # smart quote
                text = text.replace('©', '(c)')  # copyright symbol
                return text
            
            # Set email headers with cleaned text
            from_name = clean_text(self.from_name)
            from_email = clean_text(self.from_email)
            to_email = clean_text(recipient_email)
            
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to_email
            
            # Set subject based on language
            if language == "ar":
                subject = clean_text("رمز التحقق الخاص بك - السندات الوطنية")
            else:
                subject = clean_text("Your Verification Code - National Bonds")
            msg['Subject'] = subject
            
            # Create HTML and plain text content
            if language == "ar":
                text_content = f"""السندات الوطنية - فحص الصحة المالية

رمز التحقق الخاص بك: {otp_code}

ينتهي هذا الرمز خلال 5 دقائق.
لا تشارك هذا الرمز مع اي شخص.

اذا لم تطلب هذا الرمز، يرجى تجاهل هذا البريد الالكتروني."""
            else:
                text_content = f"""National Bonds - Financial Health Check

Your Verification Code: {otp_code}

This code expires in 5 minutes.
Never share this code with anyone.

If you didn't request this code, please ignore this email."""
            
            # Clean any problematic Unicode characters using the same function
            text_content = clean_text(text_content)
            
            # Generate professional HTML template
            html_content = self._generate_simple_otp_html(otp_code, language)
            # Clean HTML content as well
            html_content = clean_text(html_content)
            
            # Attach both plain text and HTML versions
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # Send email
            delivery_result = self._send_email(msg)
            
            return {
                'success': delivery_result['success'],
                'message': 'OTP sent successfully' if delivery_result['success'] else delivery_result.get('message', 'Failed to send OTP'),
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
        """Generate OTP HTML email using Jinja2 template."""
        # Debug information
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        print(f"🔍 Template directory: {template_dir}")
        print(f"🔍 Template directory exists: {os.path.exists(template_dir)}")
        print(f"🔍 Jinja env initialized: {self.jinja_env is not None}")
        
        if self.jinja_env is None:
            print("⚠️ Jinja2 environment is None, using fallback")
            return self._generate_fallback_otp_html(otp_code, language)
        
        try:
            # Try to load the Jinja2 template
            template_name = f"otp_email_{language}.html"
            print(f"🔍 Loading template: {template_name}")
            
            # List available templates for debugging
            template_files = os.listdir(template_dir) if os.path.exists(template_dir) else []
            print(f"🔍 Available templates: {template_files}")
            
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(otp_code=otp_code)
            print(f"✅ Template loaded successfully: {template_name}")
            return html_content
        except Exception as e:
            print(f"❌ Could not load template {template_name}: {e}")
            print(f"❌ Exception type: {type(e)}")
            # Fallback to hardcoded HTML
            return self._generate_fallback_otp_html(otp_code, language)
    
    def _generate_fallback_otp_html(self, otp_code: str, language: str) -> str:
        """Generate simple OTP HTML email fallback when template is not available."""
        # Get frontend URL for logos
        frontend_url = settings.base_url
        
        if language == "ar":
            # Generate individual digit boxes for Arabic
            otp_digits_html = ""
            for digit in otp_code:
                otp_digits_html += f'''
                <div style="display: inline-block; width: 60px; height: 70px; border: 2px solid #437749; border-radius: 8px; font-size: 32px; font-weight: 600; color: #1a1a1a; background-color: #ffffff; text-align: center; line-height: 66px; margin: 0 4px; vertical-align: top;">
                    {digit}
                </div>'''
            
            return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رمز التحقق الخاص بك - صكوك الوطنية</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ margin: 0; padding: 0; font-family: "Segoe UI", "Arial", sans-serif; line-height: 1.8; color: #505d68; background-color: #f5f5f5; direction: rtl; }}
        .email-wrapper {{ width: 100%; background-color: #f5f5f5; padding: 40px 0; }}
        .email-container {{ width: 50%; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }}
        .header {{ background-color: #ffffff; padding: 30px 40px 20px 40px; }}
        .content {{ padding: 40px; }}
        .footer {{ background-color: #ffffff; display: flex; justify-content: space-between; align-items: center; padding: 30px 40px; border-top: 1px solid #f0f0f0; }}
        @media only screen and (max-width: 600px) {{
            .email-container {{ width: 95%; }}
            .content {{ padding: 30px 20px; }}
            .header {{ padding: 20px; }}
            .footer {{ flex-direction: column; gap: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="email-container">
            <!-- Header -->
            <div class="header" style="width: 100%; display: flex; justify-content: center;">
                <div class="logo">
                    <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332361/financial_clinic_nep6cd.png" alt="Financial Clinic" style="height: 40px;" />
                </div>
            </div>

            <!-- Content -->
            <div class="content">
                <div style="font-size: 16px; color: #505d68; margin-bottom: 20px; font-weight: 400;">أهلاً وسهلاً،</div>

                <div style="font-size: 15px; color: #505d68; margin-bottom: 30px; line-height: 1.8;">
                    شكراً لك على استخدام فحص الصحة المالية من السندات الوطنية. للتحقق من عنوان بريدك الإلكتروني وتأمين حسابك، يرجى استخدام رمز التحقق أدناه:
                </div>

                <!-- Verification Code -->
                <div style="text-align: center; margin: 40px 0;">
                    <div style="font-size: 14px; color: #6b7280; margin-bottom: 20px; font-weight: 500;">رمز التحقق</div>
                    <div style="text-align: center; margin: 0 auto; width: 100%;">
                        {otp_digits_html}
                    </div>
                </div>

                <div style="font-size: 14px; color: #6b7280; margin-top: 30px; line-height: 1.8;">
                    أدخل هذا الرمز في التطبيق لإكمال التحقق. إذا لم تطلب هذا الرمز، يمكنك تجاهل هذا البريد الإلكتروني بأمان.
                </div>
            </div>

         <!-- Footer -->
<div class="footer" style="display: flex; justify-content: space-between; align-items: center; ">
    <!-- LEFT: Logo -->
    <div class="footer-logo">
        <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764334328/logo_bhsixi.png" 
             alt="National Bonds" />
        <div>
            SAVE.INVEST.<span style="color: #b8985f;">PROSPER.</span>
        </div>
    </div>

    <!-- CENTER: Social Icons -->
    <div>
        <div>
            STAY CONNECTED
        </div>

        <div ">
            <a href="https://https://www.facebook.com/nationalbonds" 
               style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #b8985f; 
                      display: inline-flex; align-items: center; justify-content: center; 
                      text-decoration: none; background-color: transparent; padding: 8px;">
                <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332010/grommet-icons_facebook-option_ukdarn.png" 
                     alt="Facebook" style="width: 24px; height: 24px;" />
            </a>

            <a href="https://www.instagram.com/nationalbonds/" 
               style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #b8985f; 
                      display: inline-flex; align-items: center; justify-content: center; 
                      text-decoration: none; background-color: transparent; padding: 8px;">
                <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764333399/instagram_khxfre.png" 
                     alt="Instagram" style="width: 24px; height: 24px;" />
            </a>

            <a href="https://www.linkedin.com/company/national-bonds-corporation" 
               style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #b8985f; 
                      display: inline-flex; align-items: center; justify-content: center; 
                      text-decoration: none; background-color: transparent; padding: 8px;">
                <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764333370/linkedin_uxkfhj.png" 
                     alt="LinkedIn" style="width: 24px; height: 24px;" />
            </a>

            <a href="https://www.youtube.com/user/NationalBondsDubai/videos" 
               style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #b8985f; 
                      display: inline-flex; align-items: center; justify-content: center; 
                      text-decoration: none; background-color: transparent; padding: 8px;">
                <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/youtube_ftgawy.png" 
                     alt="YouTube" style="width: 24px; height: 24px;" />
            </a>
        </div>
    </div>

    <!-- RIGHT: App + Branches -->
   <!-- App/Branches Right -->
                        <td align="center" style="vertical-align:middle; padding-right:30px;">
                            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
                                <tr>
                                    <td style="padding:0 18px; text-align:center; vertical-align:top;">
                                       <span style="display:inline-block; width:32px;margin-bottom: 10px; height:32px; border-radius:50%; border:2px solid #b8985f; background:#fff; display:flex; align-items:center; justify-content:center; padding:4px; box-sizing:border-box;">
  <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/downlaod_tzobjf.png" alt="Download App" style="width:18px; height:18px; display:block;" />
</span>
                                        <div style="font-size:10px; color:#6b7280;">DOWNLOAD OUR APP</div>
                                    </td>
                                    <td style="padding:0 18px; text-align:center; vertical-align:top;">
                                       <span style="display:inline-block; width:32px; margin-bottom: 10px;height:32px; border-radius:50%; border:2px solid #b8985f; background:#fff; display:flex; align-items:center; justify-content:center; padding:4px; box-sizing:border-box;">
  <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/location_bmwxm8.png" alt="Branches" style="width:18px; height:18px; display:block;" />
</span>
                                        <div style="font-size:10px; color:#6b7280;">OUR BRANCHES</div>
                                    </td>
                                </tr>
                            </table>
                        </td>

</div>


                <div style="display: flex; gap: 30px; flex: 0 0 auto;">
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">حمل تطبيقنا</div>
                        <div style="margin-top: 10px;">
                            <img src="https://res.cloudina https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/downlaod_tzobjf.pngry.com/dhujwbcor/image/upload/v1764332336/youtube_ftgawy.png" alt="Download" style="width: 24px; height: 24px; filter: brightness(0) saturate(100%) invert(71%) sepia(47%) saturate(414%) hue-rotate(358deg) brightness(92%) contrast(86%);" />
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 11px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">فروعنا</div>
                        <div style="margin-top: 10px;">
                            <img src="/homepage/images/Vector2.png" alt="Location" style="width: 24px; height: 24px; filter: brightness(0) saturate(100%) invert(71%) sepia(47%) saturate(414%) hue-rotate(358deg) brightness(92%) contrast(86%);" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        else:
            # Generate individual digit boxes for English
            otp_digits_html = ""
            for digit in otp_code:
                otp_digits_html += f'''
                <div style="display: inline-block; width: 60px; height: 70px; border: 2px solid #437749; border-radius: 8px; font-size: 32px; font-weight: 600; color: #1a1a1a; background-color: #ffffff; text-align: center; line-height: 66px; margin: 0 4px; vertical-align: top;">
                    {digit}
                </div>'''
            
            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Verification Code - National Bonds</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica", "Arial", sans-serif; line-height: 1.6; color: #505d68; background-color: #f5f5f5; }}
        .email-wrapper {{ width: 100%; background-color: #f5f5f5; padding: 40px 0; }}
        .email-container {{ width: 50%; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }}
        .header {{ background-color: #ffffff; padding: 30px 40px 20px 40px; }}
        .content {{ padding: 40px; width: 100%; }}
        .footer {{ background-color: #ffffff; display: flex; justify-content: space-between; align-items: center; padding: 30px 40px; border-top: 1px solid #f0f0f0; }}
        @media only screen and (max-width: 600px) {{
            .email-container {{ width: 95%; }}
            .content {{ padding: 30px 20px; }}
            .header {{ padding: 20px; }}
            .footer {{ flex-direction: column; gap: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="email-container">
            <!-- Header -->
            <div class="header" style="width: 100%; display: flex; justify-content: center;">
                <div class="logo">
                    <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332361/financial_clinic_nep6cd.png" alt="Financial Clinic" style="height: 40px;" />
                </div>
            </div>

            <!-- Content -->
            <div class="content">
                <div style="font-size: 16px; color: #505d68; margin-bottom: 20px; font-weight: 400;">Hello,</div>

                <div style="font-size: 15px; color: #505d68; margin-bottom: 30px; line-height: 1.6;">
                    Thank you for using the National Bonds Financial Health Check. To verify your email address and secure your account, please use the verification code below:
                </div>

                <!-- Verification Code -->
                <div style="text-align: center; margin: 40px 0;">
                    <div style="font-size: 14px; color: #6b7280; margin-bottom: 20px; font-weight: 500;">Verification Code</div>
                    <div style="text-align: center; margin: 0 auto; width: 100%;">
                        {otp_digits_html}
                    </div>
                </div>

                <div style="font-size: 14px; color: #6b7280; margin-top: 30px; line-height: 1.6;">
                    Enter this code in the application to complete your verification. If you didn't request this code, you can safely ignore this email.
                </div>
            </div>

            <!-- Footer -->
           <!-- Footer -->
<div class="footer" >
    
    <!-- LEFT: Logo -->
    <div class="footer-logo">
        <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764334328/logo_bhsixi.png" 
             alt="National Bonds" 
        
        <div>
            SAVE.INVEST.<span style="color: #b8985f;">PROSPER.</span>
        </div>
    </div>

    <!-- CENTER: Social Icons -->
    <div>
        <div>
            STAY CONNECTED
        </div>

        <div s>
            <a href="https://https://www.facebook.com/nationalbonds" 
               style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #b8985f; 
                      display: inline-flex; align-items: center; justify-content: center; 
                      text-decoration: none; background-color: transparent; padding: 8px;">
                <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332010/grommet-icons_facebook-option_ukdarn.png" 
                     alt="Facebook" style="width: 24px; height: 24px;" />
            </a>

            <a href="https://www.instagram.com/nationalbondsuae" 
               style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #b8985f; 
                      display: inline-flex; align-items: center; justify-content: center; 
                      text-decoration: none; background-color: transparent; padding: 8px;">
                <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764333399/instagram_khxfre.png" 
                     alt="Instagram" style="width: 24px; height: 24px;" />
            </a>

            <a href="https://www.linkedin.com/company/national-bonds-corporation" 
               style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #b8985f; 
                      display: inline-flex; align-items: center; justify-content: center; 
                      text-decoration: none; background-color: transparent; padding: 8px;">
                <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764333370/linkedin_uxkfhj.png" 
                     alt="LinkedIn" style="width: 24px; height: 24px;" />
            </a>

            <a href="https://www.youtube.com/user/NationalBondsDubai/videos" 
               style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #b8985f; 
                      display: inline-flex; align-items: center; justify-content: center; 
                      text-decoration: none; background-color: transparent; padding: 8px;">
                <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/youtube_ftgawy.png" 
                     alt="YouTube" style="width: 24px; height: 24px;" />
            </a>
        </div>
    </div>

    <!-- RIGHT: App + Branches -->
    <!-- App/Branches Right -->
                        <td align="center" style="vertical-align:middle; padding-right:30px;">
                            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
                                <tr>
                                    <td style="padding:0 18px; text-align:center; vertical-align:top;">
                                       <span style="display:inline-block; width:32px;margin-bottom: 10px; height:32px; border-radius:50%; border:2px solid #b8985f; background:#fff; display:flex; align-items:center; justify-content:center; padding:4px; box-sizing:border-box;">
  <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/downlaod_tzobjf.png" alt="Download App" style="width:18px; height:18px; display:block;" />
</span>
                                        <div style="font-size:10px; color:#6b7280;">DOWNLOAD OUR APP</div>
                                    </td>
                                    <td style="padding:0 18px; text-align:center; vertical-align:top;">
                                       <span style="display:inline-block; width:32px; margin-bottom: 10px;height:32px; border-radius:50%; border:2px solid #b8985f; background:#fff; display:flex; align-items:center; justify-content:center; padding:4px; box-sizing:border-box;">
  <img src="https://res.cloudinary.com/dhujwbcor/image/upload/v1764332336/location_bmwxm8.png" alt="Branches" style="width:18px; height:18px; display:block;" />
</span>
                                        <div style="font-size:10px; color:#6b7280;">OUR BRANCHES</div>
                                    </td>
                                </tr>
                            </table>
                        </td>

</div>

        </div>
    </div>
</body>
</html>
"""