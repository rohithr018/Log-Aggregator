import random
import time

services = [
    "auth-service", "payment-service", "inventory-service", 
    "notification-service", "analytics-service", "gateway", "user-service"
]

log_levels = ["INFO", "DEBUG", "WARN", "ERROR", "CRITICAL"]

app_messages = [
    "User login successful",
    "User login failed due to invalid credentials",
    "Payment transaction completed",
    "Payment gateway timeout",
    "Inventory updated successfully",
    "Notification sent to user",
    "Session expired",
    "Cache refreshed successfully",
    "Rate limit exceeded for IP address",
    "External API call succeeded",
    "External API call failed with status 500"
]

metric_types = [
    "cpu_usage", "memory_usage", "disk_io", 
    "network_io", "request_latency_ms", "error_rate"
]

def generate_metrics():
    return {
        "cpu_usage": round(random.uniform(10.0, 90.0), 2),           # in %
        "memory_usage": round(random.uniform(100, 8000), 2),          # in MB
        "disk_io": round(random.uniform(100, 1000), 2),               # in MB/s
        "network_io": round(random.uniform(10, 500), 2),              # in MB/s
        "request_latency_ms": round(random.uniform(20, 500), 2),      # in ms
        "error_rate": round(random.uniform(0.0, 5.0), 2)              # in %
    }

def get_random_log():
    log_type = random.choices(["application", "metric"], weights=[0.7, 0.3])[0]  # 70% app logs, 30% metrics
    
    if log_type == "application":
        return {
            "type": "application_log",
            "application": random.choice(services),
            "level": random.choices(log_levels, weights=[50, 20, 15, 10, 5])[0],
            "message": random.choice(app_messages),
            "environment": random.choice(["production", "staging", "dev"]),
            "region": random.choice(["us-east-1", "ap-south-1", "eu-west-2"]),
            "instance_id": f"inst-{random.randint(100, 999)}",
            "user_id": random.randint(1000, 5000),
            "session_id": f"sess-{random.randint(10000, 99999)}",
            "transaction_id": f"txn-{random.randint(100000, 999999)}"
        }
    
    elif log_type == "metric":
        metrics = generate_metrics()
        return {
            "type": "system_metric",
            "application": random.choice(services),
            "cpu_usage_percent": metrics["cpu_usage"],
            "memory_usage_mb": metrics["memory_usage"],
            "disk_io_mb_s": metrics["disk_io"],
            "network_io_mb_s": metrics["network_io"],
            "avg_request_latency_ms": metrics["request_latency_ms"],
            "error_rate_percent": metrics["error_rate"],
            "environment": random.choice(["production", "staging", "dev"]),
            "region": random.choice(["us-east-1", "ap-south-1", "eu-west-2"]),
            "instance_id": f"inst-{random.randint(100, 999)}"
        }

print(get_random_log())