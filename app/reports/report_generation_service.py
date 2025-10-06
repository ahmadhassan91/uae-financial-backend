"""Report generation service that provides a unified interface for creating reports."""
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.reports.pdf_service import PDFReportService, BrandingConfig
from app.models import SurveyResponse, CustomerProfile


class ReportGenerationService:
    """
    Unified service for generating various types of reports.
    
    This service provides a high-level interface for report generation,
    supporting multiple formats, branding configurations, and languages.
    """
    
    def __init__(self):
        """Initialize the report generation service."""
        self.pdf_service = PDFReportService()
    
    async def generate_pdf_report(
        self, 
        survey_response: SurveyResponse,
        language: str = "en"
    ) -> bytes:
        """
        Generate a standard PDF report for a survey response.
        
        Args:
            survey_response: The survey response to generate a report for
            language: Language code ('en' or 'ar')
            
        Returns:
            PDF content as bytes
        """
        return self.pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=survey_response.customer_profile,
            language=language
        )
    
    async def generate_branded_pdf(
        self,
        survey_data: dict,
        branding_config: BrandingConfig,
        language: str = "en"
    ) -> bytes:
        """
        Generate a branded PDF report from survey data.
        
        Args:
            survey_data: Dictionary containing survey response and profile data
            branding_config: Branding configuration for the report
            language: Language code ('en' or 'ar')
            
        Returns:
            PDF content as bytes
        """
        return self.pdf_service.generate_branded_pdf(
            survey_data=survey_data,
            branding_config=branding_config,
            language=language
        )
    
    async def generate_summary_report(
        self,
        survey_response: SurveyResponse,
        language: str = "en"
    ) -> bytes:
        """
        Generate a condensed summary report (1-2 pages).
        
        Args:
            survey_response: The survey response to generate a report for
            language: Language code ('en' or 'ar')
            
        Returns:
            PDF content as bytes
        """
        return self.pdf_service.generate_summary_report(
            survey_response=survey_response,
            customer_profile=survey_response.customer_profile,
            language=language
        )
    
    async def generate_company_branded_report(
        self,
        survey_response: SurveyResponse,
        company_branding: Dict[str, Any],
        language: str = "en"
    ) -> bytes:
        """
        Generate a company-branded report with custom styling.
        
        Args:
            survey_response: The survey response to generate a report for
            company_branding: Company-specific branding configuration
            language: Language code ('en' or 'ar')
            
        Returns:
            PDF content as bytes
        """
        # Convert company branding dict to BrandingConfig
        branding_config = BrandingConfig(
            logo_path=company_branding.get('logo_path'),
            primary_color=company_branding.get('primary_color', '#1e3a8a'),
            secondary_color=company_branding.get('secondary_color', '#059669'),
            accent_color=company_branding.get('accent_color', '#dc2626'),
            company_name=company_branding.get('company_name', 'National Bonds'),
            website=company_branding.get('website', 'www.nationalbonds.ae'),
            footer_text=company_branding.get('footer_text'),
            show_charts=company_branding.get('show_charts', True),
            chart_style=company_branding.get('chart_style', 'modern')
        )
        
        return self.pdf_service.generate_pdf_report(
            survey_response=survey_response,
            customer_profile=survey_response.customer_profile,
            language=language,
            branding_config=branding_config
        )
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported report formats.
        
        Returns:
            List of supported format strings
        """
        return ['pdf', 'summary_pdf']
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of supported language codes
        """
        return ['en', 'ar']
    
    def create_branding_config(
        self,
        logo_path: Optional[str] = None,
        primary_color: str = "#1e3a8a",
        secondary_color: str = "#059669",
        accent_color: str = "#dc2626",
        company_name: str = "National Bonds",
        website: str = "www.nationalbonds.ae",
        footer_text: Optional[str] = None,
        show_charts: bool = True,
        chart_style: str = "modern"
    ) -> BrandingConfig:
        """
        Create a branding configuration object.
        
        Args:
            logo_path: Path to company logo image
            primary_color: Primary brand color (hex)
            secondary_color: Secondary brand color (hex)
            accent_color: Accent color for highlights (hex)
            company_name: Company name for branding
            website: Company website URL
            footer_text: Custom footer text
            show_charts: Whether to include charts in reports
            chart_style: Chart style ('modern', 'classic', 'minimal')
            
        Returns:
            BrandingConfig object
        """
        return BrandingConfig(
            logo_path=logo_path,
            primary_color=primary_color,
            secondary_color=secondary_color,
            accent_color=accent_color,
            company_name=company_name,
            website=website,
            footer_text=footer_text,
            show_charts=show_charts,
            chart_style=chart_style
        )
    
    def validate_branding_config(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate a branding configuration dictionary.
        
        Args:
            config: Branding configuration dictionary to validate
            
        Returns:
            Dictionary with validation results and any errors
        """
        errors = []
        warnings = []
        
        # Validate colors
        color_fields = ['primary_color', 'secondary_color', 'accent_color']
        for field in color_fields:
            if field in config:
                color = config[field]
                if not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
                    errors.append(f"{field} must be a valid hex color (e.g., #1e3a8a)")
        
        # Validate logo path
        if 'logo_path' in config and config['logo_path']:
            import os
            if not os.path.exists(config['logo_path']):
                warnings.append(f"Logo file not found: {config['logo_path']}")
        
        # Validate chart style
        if 'chart_style' in config:
            valid_styles = ['modern', 'classic', 'minimal']
            if config['chart_style'] not in valid_styles:
                errors.append(f"chart_style must be one of: {', '.join(valid_styles)}")
        
        # Validate website URL
        if 'website' in config and config['website']:
            website = config['website']
            if not isinstance(website, str) or not (website.startswith('http') or website.startswith('www.')):
                warnings.append("Website should be a valid URL")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def generate_report_metadata(
        self,
        survey_response: SurveyResponse,
        report_type: str = "standard",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate metadata about a report without creating the actual report.
        
        Args:
            survey_response: The survey response
            report_type: Type of report ('standard', 'summary', 'branded')
            language: Language code
            
        Returns:
            Dictionary with report metadata
        """
        metadata = {
            'report_id': f"report_{survey_response.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'survey_response_id': survey_response.id,
            'user_id': survey_response.user_id,
            'report_type': report_type,
            'language': language,
            'generated_at': datetime.now().isoformat(),
            'overall_score': survey_response.overall_score,
            'pillar_scores': {
                'budgeting': survey_response.budgeting_score,
                'savings': survey_response.savings_score,
                'debt_management': survey_response.debt_management_score,
                'financial_planning': survey_response.financial_planning_score,
                'investment_knowledge': survey_response.investment_knowledge_score
            },
            'risk_tolerance': survey_response.risk_tolerance,
            'estimated_pages': 3 if report_type == 'summary' else 5,
            'includes_charts': report_type != 'summary',
            'customer_profile': {
                'name': f"{survey_response.customer_profile.first_name} {survey_response.customer_profile.last_name}" if survey_response.customer_profile else "Unknown",
                'age': survey_response.customer_profile.age if survey_response.customer_profile else None,
                'nationality': survey_response.customer_profile.nationality if survey_response.customer_profile else None,
                'emirate': survey_response.customer_profile.emirate if survey_response.customer_profile else None
            }
        }
        
        return metadata