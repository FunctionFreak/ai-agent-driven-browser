import json
from datetime import datetime

class MetadataGenerator:
    def __init__(self):
        pass

    def generate_metadata(self, object_detections, ocr_results):
        """
        Combine YOLOv8 detections and OCR results into structured metadata.
        
        :param object_detections: List of dictionaries from YOLOv8 detector.
        :param ocr_results: List of dictionaries from the OCR processor.
        :return: Dictionary containing timestamp, object detections, and OCR results.
        """
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "object_detections": object_detections,
            "ocr_results": ocr_results
        }
        return metadata

    def save_metadata(self, metadata, file_path="metadata.json"):
        """
        Save the generated metadata to a JSON file.
        
        :param metadata: The metadata dictionary.
        :param file_path: Path where the JSON should be saved.
        """
        with open(file_path, "w") as f:
            json.dump(metadata, f, indent=2)

# Example usage:
if __name__ == "__main__":
    # Dummy data for testing
    object_detections = [
        {"bbox": [100.0, 100.0, 200.0, 200.0], "confidence": 0.95, "class": 0},
        {"bbox": [300.0, 300.0, 400.0, 400.0], "confidence": 0.90, "class": 1}
    ]
    ocr_results = [
        {"bbox": [[10.0, 10.0], [10.0, 50.0], [50.0, 50.0], [50.0, 10.0]], "text": "Hello", "confidence": 0.85},
        {"bbox": [[60.0, 60.0], [60.0, 100.0], [100.0, 100.0], [100.0, 60.0]], "text": "World", "confidence": 0.80}
    ]
    
    generator = MetadataGenerator()
    metadata = generator.generate_metadata(object_detections, ocr_results)
    print("Generated Metadata:")
    print(json.dumps(metadata, indent=2))
    generator.save_metadata(metadata)
