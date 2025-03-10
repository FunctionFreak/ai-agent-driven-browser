# File: src/vision/screenshot_analyzer.py

from PIL import Image, ImageFilter
import base64
from io import BytesIO

class ScreenshotAnalyzer:
    def __init__(self):
        pass

    def analyze_screenshot(self, screenshot_base64):
        """
        Analyze a base64-encoded screenshot.
        Decodes the image, retrieves basic metadata, and performs
        edge detection to extract additional visual context.
        
        Returns a dictionary containing:
          - Image dimensions (width, height)
          - Image format and mode
          - A simple edge analysis metric (average edge intensity)
        """
        image_data = base64.b64decode(screenshot_base64)
        image = Image.open(BytesIO(image_data))
        
        # Basic metadata
        analysis = {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode
        }
        
        # Apply edge detection filter
        edges = image.filter(ImageFilter.FIND_EDGES)
        analysis["edges_info"] = self._analyze_edges(edges)
        
        return analysis

    def _analyze_edges(self, image):
        """
        Analyze the edge-detected image.
        Converts the image to grayscale, calculates a histogram,
        and computes the average edge intensity as a simple metric.
        """
        grayscale = image.convert("L")
        histogram = grayscale.histogram()
        total_pixels = sum(histogram)
        avg_intensity = sum(i * count for i, count in enumerate(histogram)) / total_pixels
        return {"average_edge_intensity": avg_intensity}
