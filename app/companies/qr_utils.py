"""QR Code generation utilities."""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SquareGradiantColorMask
import io
import base64
from typing import Optional, Tuple
import json
from datetime import datetime


def generate_qr_code(
    url: str,
    company_id: int,
    company_name: str,
    expires_at: Optional[datetime] = None,
    size: Tuple[int, int] = (300, 300),
    include_logo: bool = False
) -> str:
    """
    Generate a QR code for a company survey link.
    
    Args:
        url: The survey URL to encode
        company_id: Company identifier
        company_name: Company name for metadata
        expires_at: Expiration timestamp
        size: QR code size (width, height)
        include_logo: Whether to include a logo overlay
        
    Returns:
        Base64 encoded PNG image of the QR code
    """
    
    # Create QR code data with metadata
    qr_data = {
        "url": url,
        "company_id": company_id,
        "company_name": company_name,
        "generated_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "type": "financial_health_survey"
    }
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls size (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size in boxes
    )
    
    # Add URL data (primary content)
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image
    if include_logo:
        # Styled QR code with gradients and rounded corners
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SquareGradiantColorMask(
                back_color=(255, 255, 255),  # White background
                center_color=(41, 128, 185),  # Blue center
                edge_color=(52, 73, 94)      # Dark blue edges
            )
        )
    else:
        # Simple black and white QR code
        img = qr.make_image(
            fill_color="black",
            back_color="white"
        )
    
    # Resize if needed
    if size != (300, 300):
        img = img.resize(size)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def generate_qr_code_file(
    url: str,
    company_id: int,
    company_name: str,
    file_path: str,
    expires_at: Optional[datetime] = None,
    size: Tuple[int, int] = (600, 600)
) -> str:
    """
    Generate and save QR code to file.
    
    Returns:
        File path where QR code was saved
    """
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create high-quality image for printing
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color="black",
        back_color="white"
    )
    
    # Resize for high quality
    img = img.resize(size)
    
    # Save to file
    img.save(file_path, format='PNG', optimize=True, quality=95)
    
    return file_path


def get_qr_code_metadata(url: str, company_id: int, expires_at: Optional[datetime] = None) -> dict:
    """Get metadata that can be embedded in QR codes."""
    return {
        "url": url,
        "company_id": company_id,
        "generated_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "format": "financial_health_survey",
        "version": "1.0"
    }
