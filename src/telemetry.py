import logging
import json
from datetime import datetime

class TelemetryService:
    def __init__(self, log_file="telemetry_log.json"):
        """
        Initialize the telemetry service.
        
        Args:
            log_file: Path to the file where telemetry data will be stored.
        """
        self.log_file = log_file
        self.records = []
        logging.info("TelemetryService initialized.")

    def record_event(self, event_type: str, details: dict):
        """
        Record a telemetry event.
        
        Args:
            event_type: A string indicating the type of event (e.g., 'navigation', 'error', 'action').
            details: A dictionary containing additional details about the event.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.records.append(event)
        logging.info(f"Telemetry event recorded: {event}")

    def save_telemetry(self):
        """
        Save all recorded telemetry data to the log file in JSON format.
        """
        try:
            with open(self.log_file, "w") as f:
                json.dump(self.records, f, indent=2)
            logging.info(f"Telemetry data saved to {self.log_file}")
        except Exception as e:
            logging.error(f"Failed to save telemetry data: {e}")

    def clear_records(self):
        """
        Clear all recorded telemetry data.
        """
        self.records = []
        logging.info("Telemetry records cleared.")
