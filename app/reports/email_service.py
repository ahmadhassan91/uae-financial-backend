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
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@nationalbonds.ae')
        self.from_name = getattr(settings, 'FROM_NAME', 'National Bonds Financial Health')
        
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
        branding_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a financial health report via email."""
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            
            # Set email headers
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            
            # Set subject based on language
            if language == "ar":
                msg['Subject'] = "تقرير تقييم الصحة المالية الخاص بك"
            else:
                msg['Subject'] = "Your Financial Health Assessment Report"
            
            # Generate email content
            html_content = self._generate_email_html(
                survey_response, customer_profile, language, branding_config
            )
            text_content = self._generate_email_text(
                survey_response, customer_profile, language
            )
            
            # Attach HTML and text versions
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # Attach PDF report
            pdf_attachment = MIMEBase('application', 'pdf')
            pdf_attachment.set_payload(pdf_content)
            encoders.encode_base64(pdf_attachment)
            
            filename = f"financial_health_report_{datetime.now().strftime('%Y%m%d')}.pdf"
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
        branding_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate HTML email content."""
        # Try to use Jinja2 template if available
        if self.jinja_env:
            try:
                template_name = f"report_email_{language}.html"
                template = self.jinja_env.get_template(template_name)
                return template.render(
                    survey_response=survey_response,
                    customer_profile=customer_profile,
                    branding_config=branding_config or {}
                )
            except:
                pass  # Fall back to inline template
        
        # Fallback to inline HTML template
        return self._get_inline_html_template(survey_response, customer_profile, language, branding_config)
    
    def _generate_email_text(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str
    ) -> str:
        """Generate plain text email content."""
        if language == "ar":
            return f"""
مرحباً {customer_profile.first_name if customer_profile else ""},

شكراً لك على إكمال تقييم الصحة المالية. نتيجتك الإجمالية هي {survey_response.overall_score}/100.

تجد مرفقاً تقريراً مفصلاً يتضمن:
• تحليل مفصل لنتائجك
• توصيات شخصية لتحسين وضعك المالي
• خطة عمل لـ 90 يوماً

لأي استفسارات، يرجى زيارة موقعنا: www.nationalbonds.ae

مع أطيب التحيات,
فريق السندات الوطنية
"""
        else:
            return f"""
Hello {customer_profile.first_name if customer_profile else ""},

Thank you for completing the Financial Health Assessment. Your overall score is {survey_response.overall_score}/100.

Please find attached your detailed report including:
• Comprehensive analysis of your results
• Personalized recommendations for improvement
• 90-day action plan

For any questions, please visit: www.nationalbonds.ae

Best regards,
National Bonds Team
"""
    
    def _get_inline_html_template(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str,
        branding_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate inline HTML template for email."""
        # Get branding colors
        primary_color = "#1e3a8a"  # National Bonds blue
        secondary_color = "#059669"  # Green for scores
        
        if branding_config:
            primary_color = branding_config.get('primary_color', primary_color)
            secondary_color = branding_config.get('secondary_color', secondary_color)
        
        # Generate score summary
        score_summary = self._generate_score_summary_html(survey_response, language)
        
        if language == "ar":
            html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير الصحة المالية</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; direction: rtl; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {primary_color}; color: white; padding: 20px; text-align: center; }}
        .score-box {{ background-color: #f8f9fa; border: 2px solid {secondary_color}; border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center; }}
        .score {{ font-size: 48px; font-weight: bold; color: {secondary_color}; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }}
        .btn {{ background-color: {primary_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>تقرير تقييم الصحة المالية</h1>
            <p>السندات الوطنية</p>
        </div>
        
        <div class="content">
            <h2>مرحباً {customer_profile.first_name if customer_profile else ""}،</h2>
            
            <p>شكراً لك على إكمال تقييم الصحة المالية. إليك ملخص نتائجك:</p>
            
            <div class="score-box">
                <div class="score">{survey_response.overall_score}</div>
                <p><strong>نتيجة الصحة المالية الإجمالية من 100</strong></p>
            </div>
            
            {score_summary}
            
            <h3>ما التالي؟</h3>
            <ul>
                <li>راجع التقرير المفصل المرفق</li>
                <li>اتبع التوصيات الشخصية</li>
                <li>ابدأ بخطة العمل لـ 90 يوماً</li>
                <li>تابع تقدمك شهرياً</li>
            </ul>
            
            <p>لأي استفسارات أو للحصول على مشورة مالية شخصية، لا تتردد في التواصل معنا.</p>
        </div>
        
        <div class="footer">
            <p>هذا التقرير لأغراض إعلامية فقط ولا يشكل نصيحة مالية.</p>
            <p>السندات الوطنية | www.nationalbonds.ae</p>
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
    <title>Financial Health Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {primary_color}; color: white; padding: 20px; text-align: center; }}
        .score-box {{ background-color: #f8f9fa; border: 2px solid {secondary_color}; border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center; }}
        .score {{ font-size: 48px; font-weight: bold; color: {secondary_color}; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }}
        .btn {{ background-color: {primary_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Financial Health Assessment Report</h1>
            <p>National Bonds</p>
        </div>
        
        <div class="content">
            <h2>Hello {customer_profile.first_name if customer_profile else ""},</h2>
            
            <p>Thank you for completing the Financial Health Assessment. Here's a summary of your results:</p>
            
            <div class="score-box">
                <div class="score">{survey_response.overall_score}</div>
                <p><strong>Overall Financial Health Score out of 100</strong></p>
            </div>
            
            {score_summary}
            
            <h3>What's Next?</h3>
            <ul>
                <li>Review your detailed report attached</li>
                <li>Follow the personalized recommendations</li>
                <li>Start with the 90-day action plan</li>
                <li>Track your progress monthly</li>
            </ul>
            
            <p>For any questions or personalized financial guidance, don't hesitate to reach out to us.</p>
        </div>
        
        <div class="footer">
            <p>This report is for informational purposes only and does not constitute financial advice.</p>
            <p>National Bonds | www.nationalbonds.ae</p>
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
        language: str = "en"
    ) -> Dict[str, Any]:
        """Send a reminder email for incomplete assessments."""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            
            if language == "ar":
                msg['Subject'] = "تذكير: أكمل تقييم صحتك المالية"
                content = self._get_reminder_content_ar(customer_name)
            else:
                msg['Subject'] = "Reminder: Complete Your Financial Health Assessment"
                content = self._get_reminder_content_en(customer_name)
            
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
    
    def _get_reminder_content_en(self, customer_name: str) -> str:
        """Get English reminder email content."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Complete Your Assessment</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2>Hello {customer_name},</h2>
        
        <p>We noticed you started the Financial Health Assessment but haven't completed it yet.</p>
        
        <p>Your financial wellness is important to us. The assessment takes just 5-10 minutes and provides valuable insights into your financial health.</p>
        
        <p><strong>Benefits of completing the assessment:</strong></p>
        <ul>
            <li>Personalized financial health score</li>
            <li>Detailed analysis of your financial situation</li>
            <li>Customized recommendations for improvement</li>
            <li>90-day action plan</li>
        </ul>
        
        <p>Ready to take control of your financial future?</p>
        
        <p>Best regards,<br>National Bonds Team</p>
    </div>
</body>
</html>
"""
    
    def _get_reminder_content_ar(self, customer_name: str) -> str:
        """Get Arabic reminder email content."""
        return f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>أكمل تقييمك</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; direction: rtl;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2>مرحباً {customer_name}،</h2>
        
        <p>لاحظنا أنك بدأت تقييم الصحة المالية ولكن لم تكمله بعد.</p>
        
        <p>صحتك المالية مهمة بالنسبة لنا. يستغرق التقييم 5-10 دقائق فقط ويوفر رؤى قيمة حول وضعك المالي.</p>
        
        <p><strong>فوائد إكمال التقييم:</strong></p>
        <ul>
            <li>نتيجة شخصية للصحة المالية</li>
            <li>تحليل مفصل لوضعك المالي</li>
            <li>توصيات مخصصة للتحسين</li>
            <li>خطة عمل لـ 90 يوماً</li>
        </ul>
        
        <p>هل أنت مستعد للسيطرة على مستقبلك المالي؟</p>
        
        <p>مع أطيب التحيات،<br>فريق السندات الوطنية</p>
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
            html_content = self._generate_financial_clinic_email_html(
                result, profile, language
            )
            text_content = self._generate_financial_clinic_email_text(
                result, profile, language
            )
            
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
        """Generate HTML email content for Financial Clinic report."""
        # Use total_score from Financial Clinic (not overall_score)
        score = result.get('total_score', result.get('overall_score', 0))
        categories = result.get('category_scores', [])
        status_band = result.get('status_band', 'Moderate')
        
        # Get primary color
        primary_color = "#1e3a8a"  # National Bonds blue
        secondary_color = "#059669"  # Green
        
        # Determine score color based on score ranges
        if score >= 81:
            score_color = "#059669"  # Green - Excellent
        elif score >= 61:
            score_color = "#3b82f6"  # Blue - Good  
        elif score >= 41:
            score_color = "#f59e0b"  # Amber - Moderate
        elif score >= 21:
            score_color = "#ef4444"  # Red - Needs Attention
        else:
            score_color = "#991b1b"  # Dark Red - At Risk
        
        # Get user name
        user_name = ""
        if profile:
            user_name = profile.get('name', '')
        
        # Build category HTML for Arabic
        categories_html_ar = ""
        for cat in categories:
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
            cat_name = cat.get('category', '')
            cat_score = cat.get('score', 0)
            cat_color = self._get_category_color(cat.get('status_level', 'moderate'))
            categories_html_en += f"""
                <div class="category">
                    <span class="category-name">{cat_name}</span>
                    <span class="category-score" style="color: {cat_color};">{cat_score:.1f}</span>
                </div>
            """
        user_name = ""
        if profile:
            user_name = profile.get('name', '')
        
        if language == "ar":
            return f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير العيادة المالية</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; direction: rtl; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {primary_color}; color: white; padding: 30px 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .score-box {{ background-color: #f8f9fa; border: 3px solid {score_color}; border-radius: 15px; padding: 30px; margin: 20px 0; text-align: center; }}
        .score {{ font-size: 64px; font-weight: bold; color: {score_color}; margin: 10px 0; }}
        .score-label {{ font-size: 18px; color: #666; }}
        .content {{ padding: 30px 20px; background: white; }}
        .category {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-right: 4px solid {secondary_color}; }}
        .category-name {{ font-weight: bold; color: {primary_color}; }}
        .category-score {{ float: left; font-size: 20px; font-weight: bold; color: {secondary_color}; }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; border-radius: 0 0 10px 10px; }}
        .highlight {{ background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        ul {{ line-height: 2; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">العيادة المالية</h1>
            <p style="margin: 10px 0; font-size: 18px;">تقرير التقييم الشخصي</p>
        </div>
        
        <div class="content">
            <h2>مرحباً {user_name}،</h2>
            
            <p>شكراً لك على إكمال تقييم العيادة المالية! نحن متحمسون لمساعدتك في تحسين صحتك المالية.</p>
            
            <div class="score-box">
                <div class="score-label">نتيجتك الإجمالية</div>
                <div class="score">{score:.1f}</div>
                <div class="score-label">من 100</div>
            </div>
            
            <div class="highlight">
                <h3 style="margin-top: 0;">📊 تفصيل النتائج حسب الفئة</h3>
                {categories_html_ar}
            </div>
            
            <h3>📄 التقرير المرفق يتضمن:</h3>
            <ul>
                <li>تحليل تفصيلي لجميع جوانب صحتك المالية</li>
                <li>توصيات شخصية مبنية على إجاباتك</li>
                <li>خطوات عملية لتحسين وضعك المالي</li>
                <li>موارد تعليمية مفيدة</li>
            </ul>
            
            <h3>🎯 الخطوات التالية:</h3>
            <ul>
                <li>راجع التقرير المفصل المرفق بعناية</li>
                <li>حدد أولوياتك المالية</li>
                <li>ابدأ بتطبيق التوصيات الأكثر تأثيراً</li>
                <li>احفظ هذا التقرير للرجوع إليه مستقبلاً</li>
            </ul>
            
            <p><strong>تذكر:</strong> تحسين صحتك المالية رحلة تتطلب الصبر والمثابرة. نحن معك في كل خطوة!</p>
        </div>
        
        <div class="footer">
            <p style="margin: 5px 0;">هذا التقرير لأغراض إعلامية فقط</p>
            <p style="margin: 5px 0; font-weight: bold;">السندات الوطنية</p>
            <p style="margin: 5px 0;">www.nationalbonds.ae</p>
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
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {primary_color}; color: white; padding: 30px 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .score-box {{ background-color: #f8f9fa; border: 3px solid {score_color}; border-radius: 15px; padding: 30px; margin: 20px 0; text-align: center; }}
        .score {{ font-size: 64px; font-weight: bold; color: {score_color}; margin: 10px 0; }}
        .score-label {{ font-size: 18px; color: #666; }}
        .content {{ padding: 30px 20px; background: white; }}
        .category {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid {secondary_color}; display: flex; justify-content: space-between; align-items: center; }}
        .category-name {{ font-weight: bold; color: {primary_color}; }}
        .category-score {{ font-size: 20px; font-weight: bold; color: {secondary_color}; }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; border-radius: 0 0 10px 10px; }}
        .highlight {{ background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        ul {{ line-height: 2; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">Financial Clinic</h1>
            <p style="margin: 10px 0; font-size: 18px;">Your Personal Assessment Report</p>
        </div>
        
        <div class="content">
            <h2>Hello {user_name},</h2>
            
            <p>Thank you for completing the Financial Clinic assessment! We're excited to help you improve your financial health.</p>
            
            <div class="score-box">
                <div class="score-label">Your Overall Score</div>
                <div class="score">{score:.1f}</div>
                <div class="score-label">out of 100</div>
            </div>
            
            <div class="highlight">
                <h3 style="margin-top: 0;">📊 Category Breakdown</h3>
                {categories_html_en}
            </div>
            
            <h3>📄 Your Attached Report Includes:</h3>
            <ul>
                <li>Detailed analysis of all aspects of your financial health</li>
                <li>Personalized recommendations based on your responses</li>
                <li>Actionable steps to improve your financial situation</li>
                <li>Helpful educational resources</li>
            </ul>
            
            <h3>🎯 Next Steps:</h3>
            <ul>
                <li>Review your detailed report attached carefully</li>
                <li>Identify your financial priorities</li>
                <li>Start implementing the most impactful recommendations</li>
                <li>Save this report for future reference</li>
            </ul>
            
            <p><strong>Remember:</strong> Improving your financial health is a journey that requires patience and persistence. We're with you every step of the way!</p>
        </div>
        
        <div class="footer">
            <p style="margin: 5px 0;">This report is for informational purposes only</p>
            <p style="margin: 5px 0; font-weight: bold;">National Bonds</p>
            <p style="margin: 5px 0;">www.nationalbonds.ae</p>
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

For inquiries: www.nationalbonds.ae

Best regards,
National Bonds Team
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