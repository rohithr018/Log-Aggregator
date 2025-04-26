import os
import re
import json
import time
import socket
import logging
import threading
from queue import Queue
from datetime import datetime
from kafka import KafkaProducer
import pytz

# Constants
DEFAULT_KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = "logs"
LOG_DIR_PATH = "/var/log"
IST = pytz.timezone("Asia/Kolkata")

class EnhancedKafkaProducer:
    def __init__(self, bootstrap_servers=DEFAULT_KAFKA_BROKER):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3,
            compression_type='gzip'
        )
        self.logger = logging.getLogger('kafka_producer')
        
    def send(self, topic, value):
        try:
            future = self.producer.send(topic, value)
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")

    def _on_send_success(self, record_metadata):
        self.logger.debug(f"Message delivered to {record_metadata.topic} [{record_metadata.partition}]")

    def _on_send_error(self, excp):
        self.logger.error(f"Message delivery failed: {excp}")

class LogFileReader:
    def __init__(self, log_dir: str, queue: Queue, shutdown_event: threading.Event):
        self.log_dir = log_dir
        self.queue = queue
        self.shutdown_event = shutdown_event
        self.hostname = socket.gethostname()
        self.logger = logging.getLogger('log_file_reader')
        self.excluded_files = {"cloud-init-output.log"}  # <== Add list of files to skip

    def _is_readable_log_file(self, filepath):
        filename = os.path.basename(filepath)
        if filename in self.excluded_files:  # <== Skip excluded files
            return False
        return os.path.isfile(filepath) and os.access(filepath, os.R_OK) and not filepath.endswith(('.gz', '.xz', '.zip', '.bz2'))

    def _parse_line(self, line, source_file):
        # Generic parsing fallback: Apr 25 14:32:01 myhost CRON[1234]: Message
        match = re.match(r"^(\w{3} +\d+ \d{2}:\d{2}:\d{2}) ([\w\-.]+) ([\w\-.\/]+)(?:\[(\d+)\])?: (.*)", line)
        if match:
            ts_str, host, app, pid, message = match.groups()
        else:
            ts_str = None
            host = self.hostname
            app = os.path.basename(source_file)
            pid = 0
            message = line.strip()

        return {
            "timestamp": datetime.now(IST).isoformat(),
            "hostname": host,
            "application": app,
            "pid": int(pid) if pid else 0,
            "level": "INFO",  # Could enhance with real detection
            "message": message,
            "metadata": {
                "source_file": source_file,
                "environment": os.getenv("ENVIRONMENT", "production"),
                "region": os.getenv("REGION", "unknown")
            }
        }

    def stream_logs(self):
        try:
            for root, _, files in os.walk(self.log_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    if not self._is_readable_log_file(filepath):
                        continue
                    try:
                        with open(filepath, 'r', errors='ignore') as f:
                            for line in f:
                                if self.shutdown_event.is_set():
                                    return
                                if line.strip():
                                    parsed = self._parse_line(line, filepath)
                                    self.queue.put(parsed)
                                    print(f"[{parsed['timestamp']}] [{parsed['application']}] [{parsed['level']}]: {parsed['message']}")
                                    time.sleep(0.01)  # Avoid flooding Kafka
                    except Exception as fe:
                        self.logger.warning(f"Failed to read {filepath}: {fe}")
        except Exception as e:
            self.logger.error(f"Error walking log directory: {e}", exc_info=True)

def kafka_sender(queue: Queue, shutdown_event: threading.Event):
    producer = EnhancedKafkaProducer()
    logger = logging.getLogger('kafka_sender')
    while not shutdown_event.is_set() or not queue.empty():
        try:
            record = queue.get(timeout=1)
            producer.send(TOPIC_NAME, record)
            queue.task_done()
        except Exception:
            continue

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    log_queue = Queue()
    shutdown_event = threading.Event()

    try:
        reader = LogFileReader(LOG_DIR_PATH, log_queue, shutdown_event)
        reader_thread = threading.Thread(target=reader.stream_logs)
        reader_thread.start()

        sender_thread = threading.Thread(target=kafka_sender, args=(log_queue, shutdown_event))
        sender_thread.start()

        logger.info("Log file reader started. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        shutdown_event.set()
        reader_thread.join()
        log_queue.join()
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logger.info("Shutdown complete.")
