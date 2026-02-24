import asyncio
from api_monitor import check_apis_async
from system_monitor import check_system
from log_analyzer import analyze_logs
from db import init_db
from alerts import evaluate_alerts

def run_cycle():
    init_db()

    api_results = asyncio.run(check_apis_async())
    cpu, ram = check_system()
    errors, infos = analyze_logs()
    alerts = evaluate_alerts(api_results, cpu, ram)

    return {
        "api_results": api_results,
        "cpu": cpu,
        "ram": ram,
        "errors": errors,
        "infos": infos,
        "alerts": alerts
    }

if __name__ == "__main__":
    results = run_cycle()
    print(results)