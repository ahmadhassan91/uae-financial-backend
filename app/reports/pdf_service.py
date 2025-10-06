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

from app.models import SurveyResponse, CustomerProfile, Recommendation
from app.surveys.scoring import SurveyScorer
from app.surveys.recommendations import RecommendationEngine


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