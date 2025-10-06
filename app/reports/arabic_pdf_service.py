"""Enhanced PDF report generation service with Arabic font support and RTL rendering."""
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
from reportlab.pdfbase.pdfutils import ImageReader
from bidi.algorithm import get_display
import arabic_reshaper

from app.models import SurveyResponse, CustomerProfile, Recommendation
from app.surveys.scoring import SurveyScorer
from app.surveys.recommendations import RecommendationEngine
from app.localization.service import LocalizationService


class ArabicBrandingConfig:
    """Enhanced branding configuration with Arabic font support."""
    
    def __init__(
        self,
        logo_path: Optional[str] = None,
        primary_color: str = "#1e3a8a",  # National Bonds blue
        secondary_color: str = "#059669",  # Green for positive scores
        accent_color: str = "#dc2626",  # Red for areas needing improvement
        company_name: str = "National Bonds",
        company_name_ar: str = "شركة السندات الوطنية",
        website: str = "www.nationalbonds.ae",
        footer_text: Optional[str] = None,
        footer_text_ar: Optional[str] = None,
        show_charts: bool = True,
        chart_style: str = "modern",  # modern, classic, minimal
        arabic_font_path: Optional[str] = None,
        english_font_path: Optional[str] = None
    ):
        self.logo_path = logo_path
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.accent_color = accent_color
        self.company_name = company_name
        self.company_name_ar = company_name_ar
        self.website = website
        self.footer_text = footer_text
        self.footer_text_ar = footer_text_ar
        self.show_charts = show_charts
        self.chart_style = chart_style
        self.arabic_font_path = arabic_font_path
        self.english_font_path = english_font_path


class ArabicPDFReportService:
    """Enhanced PDF report service with Arabic font support and RTL rendering."""
    
    def __init__(self, branding_config: Optional[ArabicBrandingConfig] = None):
        """Initialize the Arabic PDF report service."""
        self.scorer = SurveyScorer()
        self.recommendation_engine = RecommendationEngine()
        self.styles = getSampleStyleSheet()
        self.branding = branding_config or ArabicBrandingConfig()
        self._register_fonts()
        self._setup_custom_styles()
    
    def _register_fonts(self):
        """Register Arabic and English fonts for PDF generation."""
        try:
            # Register Arabic fonts (using system fonts or bundled fonts)
            arabic_fonts = [
                ('NotoSansArabic', 'NotoSansArabic-Regular.ttf'),
                ('NotoSansArabic-Bold', 'NotoSansArabic-Bold.ttf'),
                ('Amiri', 'Amiri-Regular.ttf'),
                ('Amiri-Bold', 'Amiri-Bold.ttf'),
                ('Cairo', 'Cairo-Regular.ttf'),
                ('Cairo-Bold', 'Cairo-Bold.ttf')
            ]
            
            # Try to register fonts from common system locations
            font_paths = [
                '/System/Library/Fonts/',  # macOS
                '/usr/share/fonts/',       # Linux
                'C:/Windows/Fonts/',       # Windows
                './fonts/',                # Local fonts directory
                os.path.join(os.path.dirname(__file__), 'fonts/')  # Relative to this file
            ]
            
            self.arabic_font = 'Helvetica'  # Fallback
            self.arabic_font_bold = 'Helvetica-Bold'  # Fallback
            
            for font_name, font_file in arabic_fonts:
                for font_path in font_paths:
                    full_path = os.path.join(font_path, font_file)
                    if os.path.exists(full_path):
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, full_path))
                            if 'Bold' in font_name:
                                self.arabic_font_bold = font_name
                            else:
                                self.arabic_font = font_name
                            print(f"Registered font: {font_name} from {full_path}")
                            break
                        except Exception as e:
                            print(f"Failed to register font {font_name}: {e}")
                            continue
            
            print(f"Using Arabic font: {self.arabic_font}")
            print(f"Using Arabic bold font: {self.arabic_font_bold}")
            
        except Exception as e:
            print(f"Error registering fonts: {e}")
            # Use default fonts as fallback
            self.arabic_font = 'Helvetica'
            self.arabic_font_bold = 'Helvetica-Bold'
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for both English and Arabic."""
        # English styles
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor(self.branding.primary_color),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Arabic styles
        self.styles.add(ParagraphStyle(
            name='ReportTitleAR',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor(self.branding.primary_color),
            alignment=TA_CENTER,
            fontName=self.arabic_font_bold
        ))
        
        # Section headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=HexColor(self.branding.primary_color),
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeaderAR',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=HexColor(self.branding.primary_color),
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8,
            fontName=self.arabic_font_bold,
            alignment=TA_RIGHT
        ))
        
        # Body text styles
        self.styles.add(ParagraphStyle(
            name='BodyTextAR',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName=self.arabic_font,
            alignment=TA_RIGHT,
            spaceBefore=6,
            spaceAfter=6
        ))
        
        # Score styles
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=HexColor(self.branding.secondary_color),
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Recommendation styles
        self.styles.add(ParagraphStyle(
            name='RecommendationTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.branding.primary_color),
            spaceBefore=10,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RecommendationTitleAR',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.branding.primary_color),
            spaceBefore=10,
            spaceAfter=5,
            fontName=self.arabic_font_bold,
            alignment=TA_RIGHT
        ))
    
    def _process_arabic_text(self, text: str) -> str:
        """Process Arabic text for proper RTL rendering."""
        try:
            # Reshape Arabic text to handle connected letters
            reshaped_text = arabic_reshaper.reshape(text)
            # Apply bidirectional algorithm for proper RTL display
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"Error processing Arabic text: {e}")
            return text
    
    def generate_pdf_report(
        self,
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str = "en",
        branding_config: Optional[ArabicBrandingConfig] = None,
        localization_service: Optional[LocalizationService] = None
    ) -> bytes:
        """Generate a complete PDF report with Arabic support."""
        # Use provided branding config or default
        if branding_config:
            self.branding = branding_config
            self._register_fonts()
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
        
        # Create a BytesIO buffer to hold the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document with RTL support if Arabic
        if language == 'ar':
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,  # Larger right margin for Arabic
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
                title=self._process_arabic_text("تقرير الصحة المالية")
            )
        else:
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
                title="Financial Health Report"
            )
        
        # Build the story (content) for the PDF
        story = []
        
        # Add header with branding
        story.extend(self._create_header(language))
        
        # Add executive summary
        story.extend(self._create_executive_summary(
            survey_response, customer_profile, language, localization_service
        ))
        
        # Add detailed scores
        story.extend(self._create_detailed_scores(
            survey_response, language, localization_service
        ))
        
        # Add recommendations
        story.extend(self._create_recommendations_section(
            survey_response, customer_profile, language, localization_service
        ))
        
        # Add footer
        story.extend(self._create_footer(language))
        
        # Build the PDF
        doc.build(story)
        
        # Get the PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _create_header(self, language: str) -> List[Any]:
        """Create the header section with logo and title."""
        story = []
        
        # Add logo if available
        if self.branding.logo_path and os.path.exists(self.branding.logo_path):
            try:
                logo = Image(self.branding.logo_path, width=2*inch, height=0.8*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 20))
            except Exception as e:
                print(f"Error adding logo: {e}")
        
        # Add title
        if language == 'ar':
            title_text = self._process_arabic_text("تقرير الصحة المالية")
            title = Paragraph(title_text, self.styles['ReportTitleAR'])
        else:
            title = Paragraph("Financial Health Assessment Report", self.styles['ReportTitle'])
        
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Add company name
        if language == 'ar':
            company_text = self._process_arabic_text(self.branding.company_name_ar)
            company = Paragraph(company_text, self.styles['SectionHeaderAR'])
        else:
            company = Paragraph(self.branding.company_name, self.styles['SectionHeader'])
        
        story.append(company)
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_executive_summary(
        self, 
        survey_response: SurveyResponse, 
        customer_profile: CustomerProfile,
        language: str,
        localization_service: Optional[LocalizationService] = None
    ) -> List[Any]:
        """Create the executive summary section."""
        story = []
        
        # Section header
        if language == 'ar':
            header_text = self._process_arabic_text("الملخص التنفيذي")
            header = Paragraph(header_text, self.styles['SectionHeaderAR'])
        else:
            header = Paragraph("Executive Summary", self.styles['SectionHeader'])
        
        story.append(header)
        
        # Overall score
        overall_score = int(survey_response.overall_score)
        score_paragraph = Paragraph(f"{overall_score}/100", self.styles['ScoreStyle'])
        story.append(score_paragraph)
        
        # Score interpretation
        if language == 'ar':
            if overall_score >= 80:
                interpretation = self._process_arabic_text("ممتاز - صحة مالية قوية")
            elif overall_score >= 60:
                interpretation = self._process_arabic_text("جيد - صحة مالية مقبولة")
            elif overall_score >= 40:
                interpretation = self._process_arabic_text("يحتاج تحسين - هناك مجال للتطوير")
            else:
                interpretation = self._process_arabic_text("يحتاج اهتمام عاجل - صحة مالية ضعيفة")
            
            interp_paragraph = Paragraph(interpretation, self.styles['BodyTextAR'])
        else:
            if overall_score >= 80:
                interpretation = "Excellent - Strong financial health"
            elif overall_score >= 60:
                interpretation = "Good - Acceptable financial health"
            elif overall_score >= 40:
                interpretation = "Needs Improvement - Room for development"
            else:
                interpretation = "Needs Urgent Attention - Weak financial health"
            
            interp_paragraph = Paragraph(interpretation, self.styles['Normal'])
        
        story.append(interp_paragraph)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_detailed_scores(
        self, 
        survey_response: SurveyResponse,
        language: str,
        localization_service: Optional[LocalizationService] = None
    ) -> List[Any]:
        """Create the detailed scores section with pillar breakdown."""
        story = []
        
        # Section header
        if language == 'ar':
            header_text = self._process_arabic_text("تفصيل النتائج")
            header = Paragraph(header_text, self.styles['SectionHeaderAR'])
        else:
            header = Paragraph("Detailed Results", self.styles['SectionHeader'])
        
        story.append(header)
        
        # Create table data for pillar scores
        if language == 'ar':
            table_data = [
                [self._process_arabic_text("النتيجة"), self._process_arabic_text("المجال")]
            ]
            
            # Add pillar scores (in Arabic)
            pillars_ar = {
                'budgeting_score': 'إدارة الميزانية',
                'savings_score': 'الادخار',
                'debt_management_score': 'إدارة الديون',
                'financial_planning_score': 'التخطيط المالي',
                'investment_knowledge_score': 'المعرفة الاستثمارية'
            }
            
            for field, name_ar in pillars_ar.items():
                score = getattr(survey_response, field, 0)
                table_data.append([
                    f"{int(score)}/100",
                    self._process_arabic_text(name_ar)
                ])
        else:
            table_data = [
                ["Pillar", "Score"]
            ]
            
            # Add pillar scores (in English)
            pillars_en = {
                'budgeting_score': 'Budgeting & Expenses',
                'savings_score': 'Savings Habit',
                'debt_management_score': 'Debt Management',
                'financial_planning_score': 'Financial Planning',
                'investment_knowledge_score': 'Investment Knowledge'
            }
            
            for field, name_en in pillars_en.items():
                score = getattr(survey_response, field, 0)
                table_data.append([name_en, f"{int(score)}/100"])
        
        # Create and style the table
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        
        if language == 'ar':
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), self.arabic_font_bold),
                ('FONTNAME', (0, 1), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
            ]))
        else:
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
            ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_recommendations_section(
        self, 
        survey_response: SurveyResponse,
        customer_profile: CustomerProfile,
        language: str,
        localization_service: Optional[LocalizationService] = None
    ) -> List[Any]:
        """Create the recommendations section."""
        story = []
        
        # Section header
        if language == 'ar':
            header_text = self._process_arabic_text("التوصيات المخصصة")
            header = Paragraph(header_text, self.styles['SectionHeaderAR'])
        else:
            header = Paragraph("Personalized Recommendations", self.styles['SectionHeader'])
        
        story.append(header)
        
        # Get recommendations
        recommendations = survey_response.recommendations
        
        if not recommendations:
            # Generate basic recommendations if none exist
            if language == 'ar':
                no_rec_text = self._process_arabic_text("لا توجد توصيات محددة متاحة حالياً.")
                no_rec = Paragraph(no_rec_text, self.styles['BodyTextAR'])
            else:
                no_rec = Paragraph("No specific recommendations available at this time.", self.styles['Normal'])
            story.append(no_rec)
        else:
            for i, rec in enumerate(recommendations[:5], 1):  # Limit to top 5 recommendations
                if language == 'ar':
                    # Try to get Arabic version of recommendation
                    if localization_service:
                        try:
                            arabic_recs = localization_service.get_recommendations_by_language(
                                [{"id": rec.category, "title": rec.title, "description": rec.description}],
                                "ar"
                            )
                            if arabic_recs:
                                title_text = self._process_arabic_text(arabic_recs[0].get("title", rec.title))
                                desc_text = self._process_arabic_text(arabic_recs[0].get("description", rec.description))
                            else:
                                title_text = self._process_arabic_text(rec.title)
                                desc_text = self._process_arabic_text(rec.description)
                        except:
                            title_text = self._process_arabic_text(rec.title)
                            desc_text = self._process_arabic_text(rec.description)
                    else:
                        title_text = self._process_arabic_text(rec.title)
                        desc_text = self._process_arabic_text(rec.description)
                    
                    title_paragraph = Paragraph(f"{i}. {title_text}", self.styles['RecommendationTitleAR'])
                    desc_paragraph = Paragraph(desc_text, self.styles['BodyTextAR'])
                else:
                    title_paragraph = Paragraph(f"{i}. {rec.title}", self.styles['RecommendationTitle'])
                    desc_paragraph = Paragraph(rec.description, self.styles['Normal'])
                
                story.append(title_paragraph)
                story.append(desc_paragraph)
                story.append(Spacer(1, 15))
        
        return story
    
    def _create_footer(self, language: str) -> List[Any]:
        """Create the footer section."""
        story = []
        
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 10))
        
        # Footer text
        if language == 'ar':
            footer_text = self.branding.footer_text_ar or self._process_arabic_text(
                f"تم إنشاء هذا التقرير بواسطة {self.branding.company_name_ar} - {self.branding.website}"
            )
            footer = Paragraph(footer_text, self.styles['BodyTextAR'])
        else:
            footer_text = self.branding.footer_text or f"Generated by {self.branding.company_name} - {self.branding.website}"
            footer = Paragraph(footer_text, self.styles['Normal'])
        
        story.append(footer)
        
        # Generation timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if language == 'ar':
            timestamp_text = self._process_arabic_text(f"تاريخ الإنشاء: {timestamp}")
            timestamp_paragraph = Paragraph(timestamp_text, self.styles['BodyTextAR'])
        else:
            timestamp_paragraph = Paragraph(f"Generated on: {timestamp}", self.styles['Normal'])
        
        story.append(Spacer(1, 5))
        story.append(timestamp_paragraph)
        
        return story


# Convenience function for easy usage
def generate_arabic_pdf_report(
    survey_response: SurveyResponse,
    customer_profile: CustomerProfile,
    language: str = "en",
    branding_config: Optional[ArabicBrandingConfig] = None,
    localization_service: Optional[LocalizationService] = None
) -> bytes:
    """Generate a PDF report with Arabic support."""
    service = ArabicPDFReportService(branding_config)
    return service.generate_pdf_report(
        survey_response, 
        customer_profile, 
        language, 
        branding_config,
        localization_service
    )