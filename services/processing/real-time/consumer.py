from kafka import KafkaConsumer
import json

# Kafka consumer: Consume logs from the 'processed-logs' topic
consumer = KafkaConsumer(
    'processed-logs',  # Topic name
    bootstrap_servers='localhost:9092',  # Kafka brokers
    group_id='dummy-consumer-group',  # Consumer group id
    auto_offset_reset='latest',  # Start from the latest message
    enable_auto_commit=True,  # Enable auto commit of offsets
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # Deserialize the JSON message
)

print("🚀 Dummy consumer started...")

# Consume and print the logs
for msg in consumer:
    log = msg.value  # The log is in JSON format
    print(f"Received log: {log}")
    # Example: Print relevant information
    print(f"Timestamp: {log['timestamp']}, Hostname: {log['hostname']}, Application: {log['application']}, Level: {log['level']}")
    print(f"Message: {log['message']}")
    print(f"System Metrics - CPU: {log['cpu']}%, Memory: {log['memory']}%, Disk: {log['disk']}%")
    print("-" * 60)
