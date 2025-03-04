import easyocr

class OCRProcessor:
    def __init__(self, languages=None):
        """
        Initialize the EasyOCR reader.
        
        :param languages: List of language codes (e.g., ['en']). Defaults to English.
        """
        if languages is None:
            languages = ['en']
        # Use GPU if available; otherwise, set gpu=False
        self.reader = easyocr.Reader(languages, gpu=True)

    def process_image(self, image_path: str):
        """
        Process the image to extract text along with bounding boxes and confidence scores.
        
        :param image_path: Path to the image file.
        :return: List of dictionaries containing text, bounding box, and confidence score.
        """
        results = self.reader.readtext(image_path)
        ocr_results = []
        for res in results:
            bbox, text, confidence = res
            # Convert each coordinate in the bbox to a Python float
            converted_bbox = [[float(x), float(y)] for (x, y) in bbox]
            ocr_results.append({
                "bbox": converted_bbox,
                "text": text,
                "confidence": float(confidence)
            })
        return ocr_results

# Example usage:
if __name__ == "__main__":
    ocr_processor = OCRProcessor()
    image_path = "screenshot_123456.png"  # Replace with your screenshot
    results = ocr_processor.process_image(image_path)
    print("OCR Results:", results)
