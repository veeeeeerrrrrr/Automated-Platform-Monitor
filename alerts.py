def evaluate_alerts(api_results, cpu, ram):
    alerts = []

    for url, status, latency in api_results:
        if status != "UP":
            alerts.append(f"ALERT: {url} is DOWN")

        if latency > 2000:
            alerts.append(f"ALERT: High latency on {url}")

    if cpu > 80:
        alerts.append("ALERT: High CPU usage")

    if ram > 80:
        alerts.append("ALERT: High RAM usage")

    return alerts