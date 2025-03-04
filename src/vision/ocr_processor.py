import easyocr
import logging

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
        Process the image to extract text with special focus on UI elements.
        
        :param image_path: Path to the image file.
        :return: List of dictionaries containing text, bounding box, and confidence score.
        """
        try:
            # Use EasyOCR with improved parameters for web content
            results = self.reader.readtext(
                image_path,
                detail=1,
                paragraph=False,
                contrast_ths=0.1,
                adjust_contrast=0.5,
                text_threshold=0.3,  # Lower threshold to catch more text
                link_threshold=0.3
            )
            
            ocr_results = []
            important_texts = []
            
            for res in results:
                bbox, text, confidence = res
                converted_bbox = [[float(x), float(y)] for (x, y) in bbox]
                
                # Check if text contains important keywords for consent forms, buttons, etc.
                text_lower = text.lower()
                important_keywords = [
                    "accept", "agree", "consent", "continue", "sign in", "reject", 
                    "search", "submit", "next", "click", "cookie", "allow"
                ]
                
                is_important = any(keyword in text_lower for keyword in important_keywords)
                
                if is_important:
                    important_texts.append(text)
                    logging.info(f"Found important UI text: '{text}' (conf: {confidence:.2f})")
                
                # Include text if it's important or meets basic criteria
                if is_important or (len(text.strip()) > 1 and confidence > 0.2):
                    ocr_results.append({
                        "bbox": converted_bbox,
                        "text": text,
                        "confidence": float(confidence)
                    })
            
            logging.info(f"OCR extracted {len(ocr_results)} text elements")
            if important_texts:
                logging.info(f"Important UI elements found: {', '.join(important_texts)}")
            
            return ocr_results
        
        except Exception as e:
            logging.error(f"OCR processing error: {e}")
            return []

# Example usage:
if __name__ == "__main__":
    ocr_processor = OCRProcessor()
    image_path = "screenshot_123456.png"  # Replace with your screenshot
    results = ocr_processor.process_image(image_path)
    print("OCR Results:", results)
