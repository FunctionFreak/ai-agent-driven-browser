import cv2
from ultralytics import YOLO

class YOLOv8Detector:
    def __init__(self, model_variant: str = 'yolov8l.pt'):
        """
        Initialize the YOLOv8 model with the given variant.
        """
        self.model = YOLO(model_variant)

    def detect(self, image_path: str):
        """
        Perform object detection on the provided image.
        
        :param image_path: The path to the input image.
        :return: List of detections with bounding boxes, confidence scores, and class indices.
        """
        results = self.model(image_path)
        detections = []
        
        for result in results:
            for box in result.boxes:
                # Get bounding box (xyxy), confidence, and class as numpy types
                xyxy = box.xyxy.cpu().numpy()[0]
                # Convert each value in the bounding box to a float
                xyxy = [float(x) for x in xyxy]
                
                conf = float(box.conf.cpu().numpy()[0])
                cls = int(box.cls.cpu().numpy()[0])
                
                detection = {
                    'bbox': xyxy,
                    'confidence': conf,
                    'class': cls
                }
                detections.append(detection)
        return detections

# Example usage:
if __name__ == "__main__":
    detector = YOLOv8Detector(model_variant='yolov8l.pt')
    image_path = "screenshot_123456.png"  # Replace with your screenshot
    detections = detector.detect(image_path)
    print("Detections:", detections)
