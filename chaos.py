import random
from db import insert_alert


def inject_latency(url):
    insert_alert(url, "CHAOS_LATENCY", "Injected artificial latency")


def inject_failure(url):
    insert_alert(url, "CHAOS_FAILURE", "Injected simulated failure")


def random_chaos(url):
    action = random.choice(["latency", "failure"])

    if action == "latency":
        inject_latency(url)
        return "Latency injected"
    else:
        inject_failure(url)
        return "Failure injected"