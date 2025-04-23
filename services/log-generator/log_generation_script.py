import time
import random
import threading
import socket
import os
import psutil
import platform
from datetime import datetime
from pathlib import Path

hostname = socket.gethostname()

log_sources = [
    ("systemd", 2879),
    ("sshd", 985),
    ("wpa_supplicant", 986),
    ("tracker-miner-fs-3", 185321),
    ("nginx", 1452),
    ("python", os.getpid()),
    ("docker", 9001),
    ("kubelet", 1001),
    ("zabbix-agent", 777),
    ("monitor", 1111),
    ("cron", 777),
    ("kernel", 0),
    ("dbus-daemon", 1234),
    ("pulseaudio", 2222),
]

log_levels = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]

# Format like journalctl
def format_log(app, pid, message, level="INFO"):
    timestamp = datetime.now().strftime("%b %d %H:%M:%S")
    return f"{timestamp} {hostname} {app}[{pid}]: {level}: {message}"

# Generate system-based messages with log level
def get_dynamic_message():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    level = random.choices(log_levels, weights=[50, 20, 15, 10, 5])[0]

    messages = [
        (f"CPU Load Averages: {os.getloadavg()}", "INFO"),
        (f"Logged-in users: {len(psutil.users())}", "DEBUG"),
        (f"System uptime: {time.time() - psutil.boot_time():.0f}s", "INFO"),
        (f"High memory usage detected: {mem}%", "WARNING" if mem > 80 else "INFO"),
        (f"Disk usage nearing limit: {disk}%", "WARNING" if disk > 85 else "INFO"),
        (f"CPU utilization spike: {cpu}%", "CRITICAL" if cpu > 90 else "INFO"),
        (f"Service restart triggered for nginx", "INFO"),
        (f"SSH login attempt failed from 192.168.1.{random.randint(1, 255)}", "WARNING"),
        (f"Permission denied accessing /var/log/syslog", "ERROR"),
        (f"Kernel: Buffer overflow attempt detected", "CRITICAL"),
        (f"User 'rohith' executed 'sudo systemctl restart docker'", "DEBUG"),
        (f"Heartbeat check from docker container {random.randint(1000, 9999)}", "DEBUG"),
        (f"Invalid config in /etc/nginx/sites-enabled/default", "ERROR"),
        (f"Firewall dropped packet from suspicious IP", "WARNING"),
        (f"Audio device not responding", "ERROR"),
        (f"New cron job scheduled for midnight", "INFO"),
        (f"DBUS: No route to destination", "ERROR"),
        (f"Tracker indexer failed to access mounted drive", "WARNING"),
    ]
    
    message, msg_level = random.choice(messages)
    return message, msg_level if level == "INFO" else level  # blend level or override

# Emit general logs
def generate_logs():
    while True:
        app, pid = random.choice(log_sources)
        msg, level = get_dynamic_message()
        print(format_log(app, pid, msg, level))
        time.sleep(random.uniform(0.1, 0.4))

# System monitor logs (consistent)
def generate_monitor_logs():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        log = format_log("monitor", os.getpid(), f"System Monitor - CPU: {cpu:.1f}%, Memory: {mem:.1f}%", "INFO")
        print(log)
        time.sleep(2)

if __name__ == "__main__":
    threads = []

    for _ in range(5):
        t = threading.Thread(target=generate_logs)
        t.daemon = True
        t.start()
        threads.append(t)

    monitor_thread = threading.Thread(target=generate_monitor_logs)
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Log Generator Stopped]")
