import psutil
from config import CPU_THRESHOLD, RAM_THRESHOLD
from logger import log_info, log_error

def check_system():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent

    if cpu > CPU_THRESHOLD:
        log_error(f"High CPU usage: {cpu}%")
    else:
        log_info(f"CPU usage normal: {cpu}%")

    if ram > RAM_THRESHOLD:
        log_error(f"High RAM usage: {ram}%")
    else:
        log_info(f"RAM usage normal: {ram}%")

    return cpu, ram