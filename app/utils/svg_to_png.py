import base64
import cairosvg
from io import BytesIO

def svg_base64_to_png_base64(svg_base64: str, output_width: int = None, output_height: int = None) -> str:
    """
    Convert an SVG image (base64-encoded string) to a PNG image (base64-encoded string).
    
    Args:
        svg_base64: The SVG image as base64-encoded string
        output_width: Optional output width in pixels
        output_height: Optional output height in pixels
    
    Returns:
        The PNG image as base64-encoded string
    """
    svg_bytes = base64.b64decode(svg_base64)
    
    # Convert with optional size parameters
    png_bytes = cairosvg.svg2png(
        bytestring=svg_bytes,
        output_width=output_width,
        output_height=output_height
    )
    
    return base64.b64encode(png_bytes).decode('utf-8')
