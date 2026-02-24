import aiohttp
import asyncio
import time
import random
from statistics import mean
from db import insert_metric, insert_alert, fetch_history
from chaos import random_chaos


LATENCY_THRESHOLD = 800  # ms
ERROR_SPIKE_THRESHOLD = 3  # consecutive failures


# =========================
# CHAOS CONFIGURATION
# =========================

CHAOS_CONFIG = {
    "enabled": False,
    "intensity": 0.1,        # probability 0.0–1.0
    "blast_radius": 1,       # number of APIs affected
    "scheduled_until": 0     # epoch time
}


def configure_chaos(enabled=False, intensity=0.1, blast_radius=1, duration=0):
    CHAOS_CONFIG["enabled"] = enabled
    CHAOS_CONFIG["intensity"] = intensity
    CHAOS_CONFIG["blast_radius"] = blast_radius

    if duration > 0:
        CHAOS_CONFIG["scheduled_until"] = time.time() + duration
    else:
        CHAOS_CONFIG["scheduled_until"] = 0


def chaos_active():
    if not CHAOS_CONFIG["enabled"]:
        return False

    if CHAOS_CONFIG["scheduled_until"] == 0:
        return True

    return time.time() < CHAOS_CONFIG["scheduled_until"]


# =========================
# API CHECKING
# =========================

async def check_single_api(session, url, chaos_targets):
    try:
        start = time.time()

        # CHAOS INJECTION
        if chaos_active() and url in chaos_targets:
            if random.random() < CHAOS_CONFIG["intensity"]:
                result = random_chaos(url)

                if "Failure" in result:
                    insert_metric(url, "SERVER_ERROR", 0)
                    insert_alert(url, "CHAOS_FAILURE", "Simulated failure injected")
                    return (url, "SERVER_ERROR", 0)

                if "Latency" in result:
                    await asyncio.sleep(2)

        async with session.get(url, timeout=5) as response:
            latency = round((time.time() - start) * 1000, 2)

            if 200 <= response.status < 400:
                status = "UP"
            elif 400 <= response.status < 500:
                status = "CLIENT_ERROR"
            else:
                status = "SERVER_ERROR"

            insert_metric(url, status, latency)

            if latency > LATENCY_THRESHOLD:
                insert_alert(
                    url,
                    "HIGH_LATENCY",
                    f"Latency spike detected: {latency} ms"
                )

            return (url, status, latency)

    except Exception:
        insert_metric(url, "DOWN", 0)
        insert_alert(url, "DOWN", "Service unreachable")
        return (url, "DOWN", 0)


async def check_apis_async(api_list):
    if not api_list:
        return []

    chaos_targets = []

    if chaos_active():
        chaos_targets = random.sample(
            api_list,
            min(len(api_list), CHAOS_CONFIG["blast_radius"])
        )

    async with aiohttp.ClientSession() as session:
        tasks = [
            check_single_api(session, url, chaos_targets)
            for url in api_list
        ]
        results = await asyncio.gather(*tasks)

        for url, _, _ in results:
            detect_error_spike(url)

        return results


# =========================
# ERROR & RECOVERY DETECTION
# =========================

def detect_error_spike(url):
    history = fetch_history()
    recent = [row for row in history if row[0] == url][-5:]
    failures = [row for row in recent if row[1] in ("DOWN", "SERVER_ERROR")]

    if len(failures) >= ERROR_SPIKE_THRESHOLD:
        insert_alert(
            url,
            "ERROR_SPIKE",
            "Multiple consecutive failures detected"
        )


def detect_recovery(url):
    history = fetch_history()
    recent = [row for row in history if row[0] == url][-6:]

    if len(recent) < 6:
        return False

    failures = [r for r in recent[:3] if r[1] != "UP"]
    recoveries = [r for r in recent[3:] if r[1] == "UP"]

    if len(failures) >= 2 and len(recoveries) >= 2:
        insert_alert(url, "RECOVERY", "Service has recovered after instability")
        return True

    return False


# =========================
# SLA & HEALTH
# =========================

def calculate_sla(url):
    history = fetch_history()
    records = [r for r in history if r[0] == url][-50:]

    if not records:
        return 100.0

    success = [r for r in records if r[1] == "UP"]
    return round((len(success) / len(records)) * 100, 2)


def calculate_health_score(url):
    history = fetch_history()
    records = [r for r in history if r[0] == url][-20:]

    if not records:
        return 100

    latencies = [r[2] for r in records if r[2] > 0]
    avg_latency = mean(latencies) if latencies else 0

    error_count = len([r for r in records if r[1] != "UP"])

    score = 100

    if avg_latency > LATENCY_THRESHOLD:
        score -= 20

    score -= error_count * 5

    return max(score, 0)


# =========================
# SYSTEM INSTABILITY SCORE
# =========================

def calculate_instability():
    history = fetch_history()

    if not history:
        return 0

    total = len(history)
    failures = len([r for r in history if r[1] != "UP"])

    base_score = (failures / total) * 100

    recent = history[-20:]
    recent_failures = len([r for r in recent if r[1] != "UP"])

    if recent:
        recent_score = (recent_failures / len(recent)) * 100
        return round((base_score * 0.6) + (recent_score * 0.4), 2)

    return round(base_score, 2)