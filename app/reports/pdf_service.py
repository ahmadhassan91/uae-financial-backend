"""PDF report generation service using ReportLab."""
import os
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import io

# Try to import Arabic reshaping libraries
try:
    from arabic_reshaper import reshape
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

from app.models import SurveyResponse, CustomerProfile, Recommendation
from app.surveys.scoring import SurveyScorer
from app.surveys.recommendations import RecommendationEngine


def process_arabic_text(text: str) -> str:
    """
    Process Arabic text for proper display in PDFs.
    
    Args:
        text: Arabic text string
        
    Returns:
        Processed text ready for PDF rendering
    """
    if not ARABIC_SUPPORT:
        # Return original text if libraries not available
        return text
    
    try:
        # Reshape Arabic text (handles character joining)
        reshaped_text = reshape(text)
        # Apply bidirectional algorithm for RTL display
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        # Fallback to original text if processing fails
        return text


def setup_arabic_fonts():
    """
    Register Arabic-compatible fonts for PDF generation.
    
    Note: This tries to use system fonts. If not available,
    falls back to standard fonts (which won't display Arabic correctly).
    """
    try:
        # Try to register DejaVu Sans (widely available and supports Arabic)
        # Common locations on different systems
        font_paths = [
            '/System/Library/Fonts/Supplemental/DejaVuSans.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',    # Linux
            'C:\\Windows\\Fonts\\DejaVuSans.ttf',                 # Windows
            '/Library/Fonts/DejaVuSans.ttf',                       # macOS alternative
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                pdfmetrics.registerFont(TTFont('Arabic-Bold', font_path))
                return True
        
        # If DejaVu not found, try Arial Unicode
        arial_paths = [
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
            'C:\\Windows\\Fonts\\ARIALUNI.TTF',
        ]
        
        for font_path in arial_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                pdfmetrics.registerFont(TTFont('Arabic-Bold', font_path))
                return True
                
        return False
    except Exception:
        return False


# Try to setup Arabic fonts on module load
ARABIC_FONTS_AVAILABLE = setup_arabic_fonts()


class BrandingConfig:
    """Configuration class for PDF branding options."""
    
    def __init__(
        self,
        logo_path: Optional[str] = None,
        primary_color: str = "#1e3a8a",  # National Bonds blue
        secondary_color: str = "#059669",  # Green for positive scores
        accent_color: str = "#dc2626",  # Red for areas needing improvement
        company_name: str = "National Bonds",
        website: str = "www.nationalbonds.ae",
        footer_text: Optional[str] = None,
        show_charts: bool = True,
        chart_style: str = "modern"  # modern, classic, minimal
    ):
        self.logo_path = logo_path
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.accent_color = accent_color
        self.company_name = company_name
        self.website = website
        self.footer_text = footer_text
        self.show_charts = show_charts
        self.chart_style = chart_style


class PDFReportService:
    """Service for generating branded PDF reports from survey responses."""
    
    def __init__(self, branding_config: Optional[BrandingConfig] = None):
        """Initialize the PDF report service."""
        self.scorer = SurveyScorer()
        self.recommendation_engine = RecommendationEngine()
        self.styles = getSampleStyleSheet()
        self.branding = branding_config or BrandingConfig()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor(self.branding.primary_color),
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=HexColor(self.branding.primary_color),
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#374151')
        ))
        
        # Score style for large numbers
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=HexColor(self.branding.secondary_color),
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='RecommendationTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.branding.primary_color),
            spaceBefore=10,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        ))
    
    def generate_pdf_report(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str = "en",
        branding_config: Optional[BrandingConfig] = None
    ) -> bytes:
        """Generate a complete PDF report for a survey response."""
        # Use provided branding config or default
        if branding_config:
            self.branding = branding_config
            # Reset styles and recreate with new branding
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
        
        # Create a BytesIO buffer to hold the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the story (content) for the PDF
        story = []
        
        # Add header with branding
        story.extend(self._create_header(language))
        
        # Add executive summary
        story.extend(self._create_executive_summary(survey_response, customer_profile, language))
        
        # Add charts if enabled
        if self.branding.show_charts:
            story.extend(self._create_charts_section(survey_response, language))
        
        # Add detailed score breakdown
        story.extend(self._create_score_breakdown(survey_response, language))
        
        # Add pillar analysis
        story.extend(self._create_pillar_analysis(survey_response, language))
        
        # Add recommendations
        story.extend(self._create_recommendations_section(survey_response, customer_profile, language))
        
        # Add action plan
        story.extend(self._create_action_plan(survey_response, customer_profile, language))
        
        # Add footer
        story.extend(self._create_footer(language))
        
        # Build the PDF
        doc.build(story)
        
        # Get the PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _create_header(self, language: str) -> List[Any]:
        """Create the header section with branding."""
        story = []
        
        # Add logo if available
        if self.branding.logo_path:
            try:
                logo = Image(self.branding.logo_path, width=2*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 12))
            except:
                pass  # Skip logo if file not found
        
        # Add company name if no logo
        if not self.branding.logo_path:
            company_style = ParagraphStyle(
                name='CompanyName',
                parent=self.styles['Normal'],
                fontSize=18,
                textColor=HexColor(self.branding.primary_color),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(self.branding.company_name, company_style))
            story.append(Spacer(1, 12))
        
        # Add title
        title_text = "Financial Health Assessment Report" if language == "en" else "تقرير تقييم الصحة المالية"
        story.append(Paragraph(title_text, self.styles['ReportTitle']))
        
        # Add generation date
        date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y')}"
        if language == "ar":
            date_text = f"تم إنشاؤه في: {datetime.now().strftime('%d %B %Y')}"
        
        story.append(Paragraph(date_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_charts_section(self, survey_response: SurveyResponse, language: str) -> List[Any]:
        """Create charts section with visual representations of scores."""
        story = []
        
        # Section header
        header_text = "Visual Score Overview" if language == "en" else "نظرة عامة مرئية على النتائج"
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        
        # Create pie chart for score distribution
        pie_chart = self._create_score_pie_chart(survey_response, language)
        if pie_chart:
            story.append(pie_chart)
            story.append(Spacer(1, 20))
        
        # Create bar chart for pillar comparison
        bar_chart = self._create_pillar_bar_chart(survey_response, language)
        if bar_chart:
            story.append(bar_chart)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_score_pie_chart(self, survey_response: SurveyResponse, language: str) -> Optional[Drawing]:
        """Create a pie chart showing score distribution by pillar."""
        try:
            # Prepare data
            scores = [
                survey_response.budgeting_score,
                survey_response.savings_score,
                survey_response.debt_management_score,
                survey_response.financial_planning_score,
                survey_response.investment_knowledge_score
            ]
            
            labels = [
                "Budgeting" if language == "en" else "الميزانية",
                "Savings" if language == "en" else "المدخرات", 
                "Debt Mgmt" if language == "en" else "إدارة الديون",
                "Planning" if language == "en" else "التخطيط",
                "Investment" if language == "en" else "الاستثمار"
            ]
            
            # Create drawing
            drawing = Drawing(400, 300)
            
            # Create pie chart
            pie = Pie()
            pie.x = 50
            pie.y = 50
            pie.width = 200
            pie.height = 200
            pie.data = scores
            pie.labels = labels
            pie.slices.strokeWidth = 0.5
            
            # Set colors based on branding
            colors_list = [
                HexColor(self.branding.primary_color),
                HexColor(self.branding.secondary_color),
                HexColor('#f59e0b'),  # Amber
                HexColor('#8b5cf6'),  # Purple
                HexColor('#ef4444')   # Red
            ]
            
            for i, color in enumerate(colors_list):
                pie.slices[i].fillColor = color
            
            drawing.add(pie)
            
            # Add legend
            legend = Legend()
            legend.x = 280
            legend.y = 150
            legend.deltax = 60
            legend.deltay = 20
            legend.fontName = 'Helvetica'
            legend.fontSize = 10
            legend.boxAnchor = 'w'
            legend.columnMaximum = 5
            legend.strokeWidth = 1
            legend.strokeColor = colors.black
            legend.deltax = 75
            legend.deltay = 20
            legend.autoXPadding = 5
            legend.yGap = 0
            legend.dxTextSpace = 5
            legend.alignment = 'right'
            legend.dividerLines = 1|2|4
            legend.dividerOffsY = 4.5
            legend.subCols.rpad = 30
            
            legend.colorNamePairs = [(colors_list[i], labels[i]) for i in range(len(labels))]
            drawing.add(legend)
            
            return drawing
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return None
    
    def _create_pillar_bar_chart(self, survey_response: SurveyResponse, language: str) -> Optional[Drawing]:
        """Create a bar chart comparing pillar scores."""
        try:
            # Prepare data
            scores = [
                survey_response.budgeting_score,
                survey_response.savings_score,
                survey_response.debt_management_score,
                survey_response.financial_planning_score,
                survey_response.investment_knowledge_score
            ]
            
            labels = [
                "Budgeting" if language == "en" else "الميزانية",
                "Savings" if language == "en" else "المدخرات", 
                "Debt Mgmt" if language == "en" else "إدارة الديون",
                "Planning" if language == "en" else "التخطيط",
                "Investment" if language == "en" else "الاستثمار"
            ]
            
            # Create drawing
            drawing = Drawing(500, 300)
            
            # Create bar chart
            chart = VerticalBarChart()
            chart.x = 50
            chart.y = 50
            chart.height = 200
            chart.width = 400
            chart.data = [scores]
            chart.categoryAxis.categoryNames = labels
            chart.categoryAxis.labels.boxAnchor = 'ne'
            chart.categoryAxis.labels.dx = 8
            chart.categoryAxis.labels.dy = -2
            chart.categoryAxis.labels.angle = 30
            chart.categoryAxis.labels.fontName = 'Helvetica'
            chart.categoryAxis.labels.fontSize = 10
            
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = 100
            chart.valueAxis.valueStep = 20
            chart.valueAxis.labels.fontName = 'Helvetica'
            chart.valueAxis.labels.fontSize = 10
            
            # Set bar colors based on performance
            chart.bars.strokeColor = colors.black
            chart.bars.strokeWidth = 0.5
            
            # Set individual bar colors
            for i, score in enumerate(scores):
                if score >= 80:
                    chart.bars[(0, i)].fillColor = HexColor(self.branding.secondary_color)
                elif score >= 60:
                    chart.bars[(0, i)].fillColor = HexColor('#f59e0b')  # Amber
                else:
                    chart.bars[(0, i)].fillColor = HexColor(self.branding.accent_color)
            
            drawing.add(chart)
            
            return drawing
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return None
    
    def _create_executive_summary(
        self, 
        survey_response: SurveyResponse, 
        customer_profile: CustomerProfile, 
        language: str
    ) -> List[Any]:
        """Create the executive summary section."""
        story = []
        
        # Section header
        header_text = "Executive Summary" if language == "en" else "الملخص التنفيذي"
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        
        # Overall score
        score_text = f"Overall Financial Health Score: {survey_response.overall_score}/100"
        if language == "ar":
            score_text = f"نتيجة الصحة المالية الإجمالية: {survey_response.overall_score}/100"
        
        story.append(Paragraph(str(survey_response.overall_score), self.styles['ScoreStyle']))
        story.append(Paragraph(score_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Score interpretation
        interpretation = self._get_score_interpretation(survey_response.overall_score, language)
        story.append(Paragraph(interpretation, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Key highlights
        highlights = self._generate_key_highlights(survey_response, language)
        story.append(Paragraph("Key Highlights:" if language == "en" else "النقاط الرئيسية:", self.styles['SubsectionHeader']))
        
        for highlight in highlights:
            story.append(Paragraph(f"• {highlight}", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_score_breakdown(self, survey_response: SurveyResponse, language: str) -> List[Any]:
        """Create the detailed score breakdown section."""
        story = []
        
        # Section header
        header_text = "Score Breakdown by Category" if language == "en" else "تفصيل النتائج حسب الفئة"
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        
        # Create table data
        table_data = []
        
        # Table headers
        if language == "en":
            headers = ["Category", "Your Score", "Max Score", "Percentage"]
        else:
            headers = ["الفئة", "نتيجتك", "النتيجة القصوى", "النسبة المئوية"]
        
        table_data.append(headers)
        
        # Add score data
        categories = [
            ("Budgeting & Income", survey_response.budgeting_score, "إدارة الميزانية والدخل"),
            ("Savings", survey_response.savings_score, "المدخرات"),
            ("Debt Management", survey_response.debt_management_score, "إدارة الديون"),
            ("Financial Planning", survey_response.financial_planning_score, "التخطيط المالي"),
            ("Investment Knowledge", survey_response.investment_knowledge_score, "المعرفة الاستثمارية")
        ]
        
        for category_en, score, category_ar in categories:
            category_name = category_ar if language == "ar" else category_en
            percentage = f"{(score/100)*100:.0f}%"
            table_data.append([category_name, f"{score:.1f}", "100", percentage])
        
        # Create and style the table
        table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_pillar_analysis(self, survey_response: SurveyResponse, language: str) -> List[Any]:
        """Create detailed analysis of each pillar."""
        story = []
        
        # Section header
        header_text = "Detailed Analysis" if language == "en" else "التحليل المفصل"
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        
        # Recalculate scores using the new scoring system
        responses = survey_response.responses if isinstance(survey_response.responses, dict) else {}
        profile_data = {
            'children': getattr(survey_response.customer_profile, 'children', 'No') if survey_response.customer_profile else 'No'
        }
        
        detailed_scores = self.scorer.calculate_scores_v2(responses, profile_data)
        
        # Analyze each pillar
        for pillar in detailed_scores.get('pillar_scores', []):
            story.extend(self._create_pillar_section(pillar, language))
        
        return story
    
    def _create_pillar_section(self, pillar: Dict[str, Any], language: str) -> List[Any]:
        """Create a section for an individual pillar."""
        story = []
        
        # Pillar name and score
        pillar_name = pillar['name']
        pillar_score = pillar['score']
        pillar_percentage = pillar['percentage']
        
        story.append(Paragraph(pillar_name, self.styles['SubsectionHeader']))
        
        # Score display
        score_text = f"Score: {pillar_score:.1f}/5.0 ({pillar_percentage}%)"
        if language == "ar":
            score_text = f"النتيجة: {pillar_score:.1f}/5.0 ({pillar_percentage}%)"
        
        story.append(Paragraph(score_text, self.styles['Normal']))
        
        # Performance assessment
        performance = self._assess_pillar_performance(pillar_percentage, language)
        story.append(Paragraph(performance, self.styles['Normal']))
        story.append(Spacer(1, 10))
        
        return story
    
    def _create_recommendations_section(
        self, 
        survey_response: SurveyResponse, 
        customer_profile: CustomerProfile, 
        language: str
    ) -> List[Any]:
        """Create the recommendations section."""
        story = []
        
        # Section header
        header_text = "Personalized Recommendations" if language == "en" else "التوصيات الشخصية"
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        
        # Generate recommendations
        recommendations = self.recommendation_engine.generate_recommendations(survey_response, customer_profile)
        
        # Group recommendations by priority
        high_priority = [r for r in recommendations if r['priority'] == 1]
        medium_priority = [r for r in recommendations if r['priority'] == 2]
        
        # High priority recommendations
        if high_priority:
            priority_text = "High Priority Actions" if language == "en" else "الإجراءات عالية الأولوية"
            story.append(Paragraph(priority_text, self.styles['SubsectionHeader']))
            
            for rec in high_priority[:3]:  # Limit to top 3
                story.extend(self._create_recommendation_item(rec, language))
        
        # Medium priority recommendations
        if medium_priority:
            priority_text = "Additional Recommendations" if language == "en" else "توصيات إضافية"
            story.append(Paragraph(priority_text, self.styles['SubsectionHeader']))
            
            for rec in medium_priority[:3]:  # Limit to top 3
                story.extend(self._create_recommendation_item(rec, language))
        
        return story
    
    def _create_recommendation_item(self, recommendation: Dict[str, Any], language: str) -> List[Any]:
        """Create a single recommendation item."""
        story = []
        
        # Recommendation title
        story.append(Paragraph(recommendation['title'], self.styles['RecommendationTitle']))
        
        # Description
        story.append(Paragraph(recommendation['description'], self.styles['Normal']))
        
        # Action steps
        if recommendation.get('action_steps'):
            steps_text = "Action Steps:" if language == "en" else "خطوات العمل:"
            story.append(Paragraph(steps_text, self.styles['Normal']))
            
            for step in recommendation['action_steps'][:3]:  # Limit to 3 steps
                story.append(Paragraph(f"• {step}", self.styles['Normal']))
        
        story.append(Spacer(1, 10))
        
        return story
    
    def _create_action_plan(
        self, 
        survey_response: SurveyResponse, 
        customer_profile: CustomerProfile, 
        language: str
    ) -> List[Any]:
        """Create a 90-day action plan."""
        story = []
        
        # Section header
        header_text = "90-Day Action Plan" if language == "en" else "خطة العمل لـ 90 يوماً"
        story.append(Paragraph(header_text, self.styles['SectionHeader']))
        
        # Create timeline
        action_plan = self._generate_action_plan(survey_response, language)
        
        for period, actions in action_plan.items():
            story.append(Paragraph(period, self.styles['SubsectionHeader']))
            
            for action in actions:
                story.append(Paragraph(f"• {action}", self.styles['Normal']))
            
            story.append(Spacer(1, 10))
        
        return story
    
    def _create_footer(self, language: str) -> List[Any]:
        """Create the footer section."""
        story = []
        
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 10))
        
        # Custom footer text or default disclaimer
        if self.branding.footer_text:
            footer_text = self.branding.footer_text
        else:
            footer_text = (
                "This report is for informational purposes only and does not constitute financial advice. "
                "Please consult with a qualified financial advisor for personalized guidance."
            )
            if language == "ar":
                footer_text = (
                    "هذا التقرير لأغراض إعلامية فقط ولا يشكل نصيحة مالية. "
                    "يرجى استشارة مستشار مالي مؤهل للحصول على إرشادات شخصية."
                )
        
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Contact information
        contact_text = f"For more information, visit: {self.branding.website}"
        if language == "ar":
            contact_text = f"لمزيد من المعلومات، قم بزيارة: {self.branding.website}"
        
        story.append(Spacer(1, 10))
        story.append(Paragraph(contact_text, self.styles['Normal']))
        
        return story
    
    def _get_score_interpretation(self, score: float, language: str) -> str:
        """Get interpretation text for the overall score."""
        if language == "ar":
            if score >= 80:
                return "ممتاز! لديك صحة مالية قوية جداً. استمر في الممارسات الجيدة."
            elif score >= 60:
                return "جيد! لديك أساس مالي قوي مع بعض المجالات للتحسين."
            elif score >= 40:
                return "متوسط. هناك فرص كبيرة لتحسين وضعك المالي."
            else:
                return "يحتاج إلى تحسين. ركز على بناء عادات مالية أساسية قوية."
        else:
            if score >= 80:
                return "Excellent! You have very strong financial health. Keep up the good practices."
            elif score >= 60:
                return "Good! You have a solid financial foundation with some areas for improvement."
            elif score >= 40:
                return "Fair. There are significant opportunities to improve your financial situation."
            else:
                return "Needs Improvement. Focus on building strong fundamental financial habits."
    
    def _generate_key_highlights(self, survey_response: SurveyResponse, language: str) -> List[str]:
        """Generate key highlights from the survey response."""
        highlights = []
        
        # Find strongest and weakest areas
        scores = {
            'Budgeting': survey_response.budgeting_score,
            'Savings': survey_response.savings_score,
            'Debt Management': survey_response.debt_management_score,
            'Financial Planning': survey_response.financial_planning_score,
            'Investment Knowledge': survey_response.investment_knowledge_score
        }
        
        strongest = max(scores, key=scores.get)
        weakest = min(scores, key=scores.get)
        
        if language == "ar":
            highlights.append(f"أقوى مجال: {strongest} ({scores[strongest]:.1f}/100)")
            highlights.append(f"مجال للتحسين: {weakest} ({scores[weakest]:.1f}/100)")
            
            if survey_response.overall_score >= 70:
                highlights.append("لديك أساس مالي قوي")
            
            if survey_response.risk_tolerance:
                risk_map = {'low': 'منخفض', 'moderate': 'متوسط', 'high': 'عالي'}
                highlights.append(f"تحمل المخاطر: {risk_map.get(survey_response.risk_tolerance, 'متوسط')}")
        else:
            highlights.append(f"Strongest area: {strongest} ({scores[strongest]:.1f}/100)")
            highlights.append(f"Area for improvement: {weakest} ({scores[weakest]:.1f}/100)")
            
            if survey_response.overall_score >= 70:
                highlights.append("You have a strong financial foundation")
            
            if survey_response.risk_tolerance:
                highlights.append(f"Risk tolerance: {survey_response.risk_tolerance.title()}")
        
        return highlights
    
    def _assess_pillar_performance(self, percentage: float, language: str) -> str:
        """Assess performance for a pillar based on percentage."""
        if language == "ar":
            if percentage >= 80:
                return "أداء ممتاز في هذا المجال."
            elif percentage >= 60:
                return "أداء جيد مع إمكانية للتحسين."
            elif percentage >= 40:
                return "أداء متوسط، يحتاج إلى تركيز."
            else:
                return "يحتاج إلى تحسين كبير في هذا المجال."
        else:
            if percentage >= 80:
                return "Excellent performance in this area."
            elif percentage >= 60:
                return "Good performance with room for improvement."
            elif percentage >= 40:
                return "Fair performance, needs focus."
            else:
                return "Significant improvement needed in this area."
    
    def _generate_action_plan(self, survey_response: SurveyResponse, language: str) -> Dict[str, List[str]]:
        """Generate a 90-day action plan based on survey results."""
        if language == "ar":
            periods = {
                "الأيام 1-30 (البداية)": [],
                "الأيام 31-60 (البناء)": [],
                "الأيام 61-90 (التحسين)": []
            }
        else:
            periods = {
                "Days 1-30 (Foundation)": [],
                "Days 31-60 (Building)": [],
                "Days 61-90 (Optimization)": []
            }
        
        # Add actions based on weakest areas
        if survey_response.budgeting_score < 60:
            if language == "ar":
                periods["الأيام 1-30 (البداية)"].append("إنشاء ميزانية شهرية مفصلة")
                periods["الأيام 31-60 (البناء)"].append("تتبع النفقات يومياً")
                periods["الأيام 61-90 (التحسين)"].append("تحسين الميزانية بناءً على البيانات")
            else:
                periods["Days 1-30 (Foundation)"].append("Create a detailed monthly budget")
                periods["Days 31-60 (Building)"].append("Track expenses daily")
                periods["Days 61-90 (Optimization)"].append("Optimize budget based on data")
        
        if survey_response.savings_score < 60:
            if language == "ar":
                periods["الأيام 1-30 (البداية)"].append("فتح حساب توفير منفصل")
                periods["الأيام 31-60 (البناء)"].append("أتمتة التوفير الشهري")
                periods["الأيام 61-90 (التحسين)"].append("زيادة معدل التوفير")
            else:
                periods["Days 1-30 (Foundation)"].append("Open a separate savings account")
                periods["Days 31-60 (Building)"].append("Automate monthly savings")
                periods["Days 61-90 (Optimization)"].append("Increase savings rate")
        
        return periods
    
    def generate_branded_pdf(
        self,
        survey_data: dict,
        branding_config: BrandingConfig,
        language: str = "en"
    ) -> bytes:
        """Generate a branded PDF report from survey data dictionary."""
        # Create mock objects from dictionary data
        survey_response = self._create_survey_response_from_dict(survey_data)
        customer_profile = self._create_customer_profile_from_dict(survey_data.get('profile', {}))
        
        return self.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=customer_profile,
            language=language,
            branding_config=branding_config
        )
    
    def generate_summary_report(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str = "en"
    ) -> bytes:
        """Generate a condensed summary report (1-2 pages)."""
        # Temporarily disable charts for summary
        original_show_charts = self.branding.show_charts
        self.branding.show_charts = False
        
        try:
            # Create a BytesIO buffer to hold the PDF
            buffer = io.BytesIO()
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build condensed story
            story = []
            
            # Add header
            story.extend(self._create_header(language))
            
            # Add executive summary only
            story.extend(self._create_executive_summary(survey_response, customer_profile, language))
            
            # Add condensed score breakdown
            story.extend(self._create_score_breakdown(survey_response, language))
            
            # Add top 3 recommendations only
            recommendations = self.recommendation_engine.generate_recommendations(survey_response, customer_profile)
            top_recommendations = recommendations[:3]
            
            if top_recommendations:
                header_text = "Top Recommendations" if language == "en" else "أهم التوصيات"
                story.append(Paragraph(header_text, self.styles['SectionHeader']))
                
                for rec in top_recommendations:
                    story.extend(self._create_recommendation_item(rec, language))
            
            # Add footer
            story.extend(self._create_footer(language))
            
            # Build the PDF
            doc.build(story)
            
            # Get the PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        finally:
            # Restore original chart setting
            self.branding.show_charts = original_show_charts
    
    def _create_survey_response_from_dict(self, data: dict) -> SurveyResponse:
        """Create a SurveyResponse object from dictionary data."""
        # This is a helper method to convert dict data to SurveyResponse object
        # In a real implementation, you might want to use Pydantic models or similar
        class MockSurveyResponse:
            def __init__(self, data):
                self.id = data.get('id', 1)
                self.user_id = data.get('user_id', 1)
                self.customer_profile_id = data.get('customer_profile_id', 1)
                self.responses = data.get('responses', {})
                self.overall_score = data.get('overall_score', 0)
                self.budgeting_score = data.get('budgeting_score', 0)
                self.savings_score = data.get('savings_score', 0)
                self.debt_management_score = data.get('debt_management_score', 0)
                self.financial_planning_score = data.get('financial_planning_score', 0)
                self.investment_knowledge_score = data.get('investment_knowledge_score', 0)
                self.risk_tolerance = data.get('risk_tolerance', 'moderate')
                self.created_at = datetime.now()
                self.customer_profile = None
        
        return MockSurveyResponse(data)
    
    def _create_customer_profile_from_dict(self, data: dict) -> CustomerProfile:
        """Create a CustomerProfile object from dictionary data."""
        class MockCustomerProfile:
            def __init__(self, data):
                self.id = data.get('id', 1)
                self.user_id = data.get('user_id', 1)
                self.first_name = data.get('first_name', 'User')
                self.last_name = data.get('last_name', 'Name')
                self.age = data.get('age', 30)
                self.gender = data.get('gender', 'Not specified')
                self.nationality = data.get('nationality', 'UAE')
                self.emirate = data.get('emirate', 'Dubai')
                self.employment_status = data.get('employment_status', 'Full-time')
                self.monthly_income = data.get('monthly_income', '10000-15000')
                self.household_size = data.get('household_size', 1)
                self.children = data.get('children', 'No')
        
        return MockCustomerProfile(data)
    
    def generate_financial_clinic_pdf(
        self,
        result: Dict[str, Any],
        profile: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> bytes:
        """
        Generate PDF report for Financial Clinic assessment matching the results page.
        
        Args:
            result: Financial Clinic calculation result with scores and categories
            profile: Optional user profile information
            language: Language code ('en' or 'ar')
            
        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=50
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Determine font based on language
        if language == "ar" and ARABIC_FONTS_AVAILABLE:
            title_font = 'Arabic-Bold'
            body_font = 'Arabic'
            alignment = TA_RIGHT  # RTL for Arabic
        else:
            title_font = 'Helvetica-Bold'
            body_font = 'Helvetica'
            alignment = TA_LEFT
        
        # Create custom styles to match the web page
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName=title_font
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=25,
            alignment=TA_CENTER,
            fontName=body_font
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=15,
            spaceBefore=20,
            fontName=title_font,
            alignment=alignment
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=8,
            leading=14,
            textColor=colors.HexColor('#374151'),
            fontName=body_font,
            alignment=alignment
        )
        
        insight_style = ParagraphStyle(
            'InsightStyle',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=8,
            leading=14,
            leftIndent=20 if language != "ar" else 0,
            rightIndent=0 if language != "ar" else 20,
            textColor=colors.HexColor('#1e3a8a'),
            fontName=body_font,
            alignment=alignment
        )
        
        # Title Section - Updated to match new design
        if language == "ar":
            title_text = process_arabic_text("إليك درجة صحتك المالية!")
            subtitle_text = process_arabic_text("هذه لمحة سريعة، نظرة واضحة على مدى صحة أموالك اليوم")
        else:
            title_text = "Here's your Financial Health Score!"
            subtitle_text = "This is your snapshot, a clear view of how healthy your finances are today."
        
        elements.append(Paragraph(title_text, title_style))
        elements.append(Paragraph(subtitle_text, subtitle_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Main Score Display - Clean large display matching new design
        total_score = result.get('total_score', 0)
        
        # Use consistent green color for score (matching #2e9e42)
        score_color = colors.HexColor('#2e9e42')
        
        # Large score display with simple clean style
        score_style = ParagraphStyle(
            'ScoreStyle', 
            fontSize=72, 
            textColor=score_color, 
            alignment=TA_CENTER, 
            fontName='Helvetica-Bold',
            leading=80,
            spaceAfter=20
        )
        
        elements.append(Paragraph(f"<b>{round(total_score)}%</b>", score_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Financial Pillar Scores - matching the new clean design
        category_header_text = process_arabic_text("درجات الركائز المالية") if language == 'ar' else "Financial Pillar Scores"
        elements.append(Paragraph(category_header_text, heading_style))
        
        category_subtext_raw = 'أدائك عبر 7 مجالات رئيسية للصحة المالية' if language == 'ar' else 'Your performance across the 7 key areas of financial health'
        category_subtext = process_arabic_text(category_subtext_raw) if language == 'ar' else category_subtext_raw
        elements.append(Paragraph(category_subtext, subtitle_style))
        elements.append(Spacer(1, 0.1*inch))
        
        category_scores = result.get('category_scores', {})
        
        # Category name translations
        category_translations = {
            'Income Stream': {'en': 'Income Stream', 'ar': 'تدفق الدخل'},
            'Savings Habit': {'en': 'Savings Habit', 'ar': 'عادات الادخار'},
            'Emergency Savings': {'en': 'Emergency Savings', 'ar': 'مدخرات الطوارئ'},
            'Debt Management': {'en': 'Debt Management', 'ar': 'إدارة الديون'},
            'Retirement Planning': {'en': 'Retirement Planning', 'ar': 'التخطيط للتقاعد'},
            'Protecting Your Family': {'en': 'Protecting Your Family', 'ar': 'حماية عائلتك'}
        }
        
        # Status level translations
        status_translations = {
            'excellent': {'en': 'Excellent', 'ar': 'ممتاز'},
            'Excellent': {'en': 'Excellent', 'ar': 'ممتاز'},
            'good': {'en': 'Good', 'ar': 'جيد'},
            'Good': {'en': 'Good', 'ar': 'جيد'},
            'at_risk': {'en': 'At Risk', 'ar': 'في خطر'},
            'At_risk': {'en': 'At Risk', 'ar': 'في خطر'},
            'At Risk': {'en': 'At Risk', 'ar': 'في خطر'},
            'moderate': {'en': 'Moderate', 'ar': 'معتدل'},
            'Moderate': {'en': 'Moderate', 'ar': 'معتدل'},
            'needs_improvement': {'en': 'Needs Improvement', 'ar': 'يحتاج تحسين'},
            'Needs Improvement': {'en': 'Needs Improvement', 'ar': 'يحتاج تحسين'},
            'Needs_improvement': {'en': 'Needs Improvement', 'ar': 'يحتاج تحسين'}
        }
        
        # Helper function for category translation
        def getCategoryTranslation(cat_name):
            cat_data = category_translations.get(cat_name, {'en': cat_name, 'ar': cat_name})
            return process_arabic_text(cat_data['ar']) if language == 'ar' else cat_data['en']
        
        # Create category table matching the web cards
        # Create header style with proper font
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=body_style,
            fontName=title_font
        )
        
        cat_table_data = []
        header_row = [
            Paragraph('<b>' + (process_arabic_text('الفئة') if language == 'ar' else 'Category') + '</b>', header_style),
            Paragraph('<b>' + (process_arabic_text('النتيجة') if language == 'ar' else 'Score') + '</b>', header_style),
            Paragraph('<b>' + (process_arabic_text('الحالة') if language == 'ar' else 'Status') + '</b>', header_style)
        ]
        cat_table_data.append(header_row)
        
        # Handle category_scores as either list or dict
        if isinstance(category_scores, list):
            # List format from Financial Clinic
            for cat_data in category_scores:
                display_name_raw = cat_data.get('category_ar') if language == 'ar' else cat_data.get('category', '')
                display_name = process_arabic_text(display_name_raw) if language == 'ar' else display_name_raw
                cat_score = cat_data.get('score', 0)
                cat_max = cat_data.get('max_possible', 100)
                cat_status = cat_data.get('status_level', 'moderate')
                
                status_trans = status_translations.get(cat_status.title(), {'en': cat_status, 'ar': cat_status})
                status_display_raw = status_trans['ar'] if language == 'ar' else status_trans['en']
                status_display = process_arabic_text(status_display_raw) if language == 'ar' else status_display_raw
                
                cat_table_data.append([
                    Paragraph(display_name, body_style),
                    Paragraph(f"{round(cat_score)} / {round(cat_max)}", body_style),
                    Paragraph(status_display, body_style)
                ])
        else:
            # Dict format (legacy)
            for cat_name, cat_data in category_scores.items():
                cat_translation = category_translations.get(cat_name, {'en': cat_name, 'ar': cat_name})
                display_name = cat_translation['ar'] if language == 'ar' else cat_translation['en']
                
                cat_score = cat_data.get('score', 0)
                cat_max = cat_data.get('max_possible', 100)
                cat_status = cat_data.get('status_level', 'Moderate')
                
                status_trans = status_translations.get(cat_status, {'en': cat_status, 'ar': cat_status})
                status_display = status_trans['ar'] if language == 'ar' else status_trans['en']
                
                cat_table_data.append([
                    Paragraph(display_name, body_style),
                    Paragraph(f"{round(cat_score)} / {round(cat_max)}", body_style),
                    Paragraph(status_display, body_style)
                ])
        
        cat_table = Table(cat_table_data, colWidths=[3*inch, 1.2*inch, 1.3*inch])
        cat_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(cat_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Your Personalized Action Plan - matching the new box design
        insights = result.get('insights', [])
        if insights:
            action_plan_header_text = process_arabic_text("خطة عملك الشخصية") if language == 'ar' else "Your Personalized Action Plan"
            elements.append(Paragraph(action_plan_header_text, heading_style))
            
            action_plan_subtext_raw = 'التغييرات الصغيرة تحدث فرقًا كبيرًا. إليك كيفية تقوية نتيجتك' if language == 'ar' else "Small changes make big differences. Here's how to strengthen your score."
            action_plan_subtext = process_arabic_text(action_plan_subtext_raw) if language == 'ar' else action_plan_subtext_raw
            elements.append(Paragraph(action_plan_subtext, subtitle_style))
            elements.append(Spacer(1, 0.15*inch))
            
            # Create action plan box with numbered list
            action_plan_data = []
            
            # Add category header
            rec_cat_text_raw = 'فئات التوصيات:' if language == 'ar' else 'Recommendation Categories:'
            rec_cat_text = process_arabic_text(rec_cat_text_raw) if language == 'ar' else rec_cat_text_raw
            action_plan_data.append([Paragraph(f"<b>{rec_cat_text}</b>", body_style)])
            
            # Add numbered insights with category
            for idx, insight in enumerate(insights[:5], 1):  # Limit to 5
                if isinstance(insight, dict):
                    category = insight.get('category', '')
                    text = insight.get('text', str(insight))
                    category_text = getCategoryTranslation(category) if language == 'ar' else category
                    insight_text_raw = f"{idx}. {category_text}: {text}"
                else:
                    insight_text_raw = f"{idx}. {str(insight)}"
                
                insight_text = process_arabic_text(insight_text_raw) if language == 'ar' else insight_text_raw
                action_plan_data.append([Paragraph(insight_text, body_style)])
            
            action_plan_table = Table(action_plan_data, colWidths=[5*inch])
            action_plan_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT' if language != 'ar' else 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafc')),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (0, 0), 12),  # Extra padding for header
                ('BOTTOMPADDING', (0, 0), (0, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 12),  # Extra padding for last item
            ]))
            
            elements.append(action_plan_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Understanding Your Score section - 4 bands layout
        understanding_header_text = process_arabic_text("فهم نتيجتك") if language == 'ar' else "Understanding Your Score"
        elements.append(Paragraph(understanding_header_text, heading_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # 4 Score bands with colors matching the new design
        bands_data = []
        if language == 'ar':
            table_cell_style = ParagraphStyle(
                'TableCellArabic',
                parent=body_style,
                fontSize=9,
                fontName=body_font,
                alignment=TA_CENTER
            )
            
            bands_raw = [
                ['1-29', 'في خطر', 'ركز على بناء عادات مالية أساسية', '#ee3b37'],
                ['30-59', 'يحتاج إلى تحسين', 'أساس جيد، مجال للنمو', '#fead2a'],
                ['60-79', 'جيد', 'صحة مالية قوية', '#e7e229'],
                ['80-100', 'ممتاز', 'رفاهية مالية متميزة', '#57b957']
            ]
            
            for row in bands_raw:
                processed_row = [
                    Paragraph(f"<b>{row[0]}</b>", table_cell_style),
                    Paragraph(f"<b>{process_arabic_text(row[1])}</b>", table_cell_style),
                    Paragraph(process_arabic_text(row[2]), table_cell_style)
                ]
                bands_data.append(processed_row)
        else:
            table_cell_style = ParagraphStyle(
                'TableCellEnglish',
                parent=body_style,
                fontSize=9,
                fontName='Helvetica',
                alignment=TA_CENTER
            )
            
            bands_raw = [
                ['1-29', 'At Risk', 'Focus on building basic financial habits', '#ee3b37'],
                ['30-59', 'Needs Improvement', 'Good foundation, room for growth', '#fead2a'],
                ['60-79', 'Good', 'Strong financial health', '#e7e229'],
                ['80-100', 'Excellent', 'Outstanding financial wellness', '#57b957']
            ]
            
            for row in bands_raw:
                processed_row = [
                    Paragraph(f"<b>{row[0]}</b>", table_cell_style),
                    Paragraph(f"<b>{row[1]}</b>", table_cell_style),
                    Paragraph(row[2], table_cell_style)
                ]
                bands_data.append(processed_row)
        
        # Create colored cells table
        bands_table = Table(bands_data, colWidths=[1.3*inch, 1.3*inch, 2.9*inch])
        bands_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Red - At Risk
            ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#ee3b37')),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.white),
            # Orange - Needs Improvement
            ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#fead2a')),
            ('TEXTCOLOR', (0, 1), (2, 1), colors.white),
            # Yellow - Good
            ('BACKGROUND', (0, 2), (2, 2), colors.HexColor('#e7e229')),
            ('TEXTCOLOR', (0, 2), (2, 2), colors.HexColor('#374151')),
            # Green - Excellent
            ('BACKGROUND', (0, 3), (2, 3), colors.HexColor('#57b957')),
            ('TEXTCOLOR', (0, 3), (2, 3), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(bands_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Footer note matching web page
        footer_note_raw = 'هذه التوصيات مصممة خصيصاً بناءً على ملفك الشخصي وإجاباتك' if language == 'ar' else 'These recommendations are tailored based on your profile and responses'
        footer_note = process_arabic_text(footer_note_raw) if language == 'ar' else footer_note_raw
        
        footer_note_style = ParagraphStyle(
            'FooterNote',
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            fontName=body_font
        )
        elements.append(Paragraph(footer_note, footer_note_style))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            fontSize=8,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            leading=11,
            fontName=body_font
        )
        
        if language == 'ar':
            disclaimer_line1 = process_arabic_text('هذا التقرير لأغراض إعلامية فقط ولا يشكل نصيحة مالية.')
            disclaimer_line2 = process_arabic_text('للحصول على مشورة مالية شخصية، يرجى استشارة مستشار مالي مؤهل.')
            disclaimer_text = f'<i>{disclaimer_line1}<br/>{disclaimer_line2}</i>'
        else:
            disclaimer_text = (
                '<i>This report is for informational purposes only and does not constitute financial advice.<br/>' +
                'For personalized financial guidance, please consult a qualified financial advisor.</i>'
            )
        
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        
        # Build PDF
        doc.build(elements, onFirstPage=self._add_clinic_page_number, onLaterPages=self._add_clinic_page_number)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _get_clinic_score_color(self, score: float) -> colors.Color:
        """Get color based on score for Financial Clinic - matching web page colors."""
        if score >= 81:
            return colors.HexColor('#059669')  # Green - Excellent
        elif score >= 61:
            return colors.HexColor('#2563eb')  # Blue - Good
        elif score >= 41:
            return colors.HexColor('#eab308')  # Yellow - Moderate
        elif score >= 21:
            return colors.HexColor('#f97316')  # Orange - Needs Attention
        else:
            return colors.HexColor('#dc2626')  # Red - At Risk
    
    def _add_clinic_page_number(self, canvas_obj, doc):
        """Add page number to the footer for Financial Clinic reports."""
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawRightString(7.5*inch, 0.5*inch, text)
        canvas_obj.drawString(1*inch, 0.5*inch, f"Generated on {datetime.now().strftime('%B %d, %Y')}")