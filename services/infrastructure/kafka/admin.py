#!/usr/bin/env python3

from kafka.admin import KafkaAdminClient, NewTopic

# Kafka bootstrap server (update if needed)
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

def create_topic(topic_name, num_partitions=1, replication_factor=1):
    admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    topic = NewTopic(
        name=topic_name,
        num_partitions=num_partitions,
        replication_factor=replication_factor
    )

    try:
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        print(f"✅ Topic '{topic_name}' created successfully.")
    except Exception as e:
        print(f"❌ Error creating topic '{topic_name}': {e}")
    finally:
        admin_client.close()

def main():
    topics = [
        ("logs", 1, 1),
        ("processed-logs", 1, 1), #0- for real time #1- for batch
        ("alert-metrics", 1, 1),
    ]

    for topic_name, partitions, replication in topics:
        create_topic(topic_name, partitions, replication)

if __name__ == "__main__":
    main()
