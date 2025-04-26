import json
import logging
import threading
import time
import pytz
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from log_simulator import get_random_log

# Constants
KAFKA_BROKERS = "localhost:29092,localhost:39092,localhost:49092"
NUM_PARTITIONS = 5
REPLICATION_FACTOR = 3
TOPIC_NAME = "logs"
IST = pytz.timezone('Asia/Kolkata')

logging.basicConfig(level=logging.INFO)

PRODUCER_CONFIG = {
    'bootstrap.servers': KAFKA_BROKERS,
    'queue.buffering.max.messages': 1000000,
    'queue.buffering.max.kbytes': 1048576,  
    'batch.num.messages': 10000,
    'linger.ms': 5,
    'acks': 1,
    'compression.type': 'gzip',
}

def create_kafka_topic(topic_name):
    admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKERS})
    try:
        metadata = admin_client.list_topics(timeout=10)
        if topic_name not in metadata.topics:
            topic = NewTopic(
                topic=topic_name,
                num_partitions=NUM_PARTITIONS,
                replication_factor=REPLICATION_FACTOR
            )
            fs = admin_client.create_topics([topic])
            for topic, future in fs.items():
                future.result()
                print(f"Topic {topic} created successfully.")
        else:
            print(f"Topic {topic_name} already exists.")
    except Exception as e:
        print(f"Error creating topic: {e}")

class EnhancedKafkaProducer:
    def __init__(self):
        self.producer = Producer(PRODUCER_CONFIG)
        self.logger = logging.getLogger('kafka_producer')

    def send(self, topic, value):
        try:
            self.producer.produce(
                topic=topic,
                key=value.get("application", "unknown").encode('utf-8'),
                value=json.dumps(value).encode('utf-8'),
                callback=self.delivery_report
            )
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")

    def delivery_report(self, err, msg):
        if err is not None:
            self.logger.error(f"Delivery failed for record {msg.key()}: {err}")

    def flush(self):
        self.producer.flush()

def produce_log(thread_id):
    producer = EnhancedKafkaProducer()
    message_counter = 0
    last_flush_time = time.time()

    while True:
        log = get_random_log()
        # print(f"Thread {thread_id} Produced log: {log}")
        producer.send(
            topic=TOPIC_NAME, 
            value=log
        )
        message_counter += 1

        # Flush every 1000 messages OR every 2 seconds
        if message_counter >= 1000 or (time.time() - last_flush_time) >= 2:
            producer.flush()
            # print(f"Thread {thread_id} flushed {message_counter} messages")
            message_counter = 0
            last_flush_time = time.time()

def produce_data_in_parallel(num_threads):
    threads = []
    try:
        for i in range(num_threads):
            thread = threading.Thread(target=produce_log, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
    except Exception as e:
        print(f"Error creating thread: {e}")

if __name__ == "__main__":
    create_kafka_topic(TOPIC_NAME)
    num_threads = 5 
    produce_data_in_parallel(num_threads)
