# File: src/vision/processor.py

import easyocr
from ultralytics import YOLO
import base64
from io import BytesIO
from PIL import Image
import numpy as np

class VisionProcessor:
    def __init__(self, yolo_model="yolov8l.pt", ocr_languages=None):
        if ocr_languages is None:
            ocr_languages = ['en']
        # Initialize YOLOv8 model
        self.yolo_model = YOLO(yolo_model)
        # Initialize EasyOCR with GPU support if available
        self.reader = easyocr.Reader(ocr_languages, gpu=True)

    def process_screenshot(self, screenshot_base64):
        """
        Process a base64-encoded screenshot.
        - Decodes the image.
        - Runs YOLOv8 for object detection.
        - Runs EasyOCR for text extraction.
        Returns a dictionary with both object and text detections.
        """
        # Decode the screenshot from base64
        image_data = base64.b64decode(screenshot_base64)
        pil_image = Image.open(BytesIO(image_data))
        np_image = np.array(pil_image)
        
        # Run YOLOv8 detection
        yolo_results = self.yolo_model(np_image)
        detections = []
        for result in yolo_results:
            for box in result.boxes:
                # Extract bounding box coordinates, confidence, and class
                xyxy = box.xyxy.cpu().numpy()[0]
                conf = float(box.conf.cpu().numpy()[0])
                cls = int(box.cls.cpu().numpy()[0])
                detections.append({
                    'bbox': xyxy.tolist(),
                    'confidence': conf,
                    'class': cls
                })
        
        # Run OCR to extract text from the image
        ocr_results = self.reader.readtext(np_image, detail=1)
        text_detections = [{
            'bbox': [[float(x), float(y)] for (x, y) in bbox],
            'text': text,
            'confidence': float(confidence)
        } for bbox, text, confidence in ocr_results]
        
        return {
            'object_detections': detections,
            'text_detections': text_detections
        }
