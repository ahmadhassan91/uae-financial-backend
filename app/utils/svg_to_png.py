import base64
import cairosvg
from io import BytesIO

def svg_base64_to_png_base64(svg_base64: str) -> str:
    """
    Convert an SVG image (base64-encoded string) to a PNG image (base64-encoded string).
    """
    svg_bytes = base64.b64decode(svg_base64)
    png_bytes = cairosvg.svg2png(bytestring=svg_bytes)
    return base64.b64encode(png_bytes).decode('utf-8')
