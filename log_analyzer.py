from db import fetch_history


def analyze_logs():
    history = fetch_history()

    errors = len([r for r in history if r[1] in ("ERROR", "DOWN")])
    infos = len([r for r in history if r[1] == "UP"])

    total = errors + infos

    error_rate = round((errors / total) * 100, 2) if total > 0 else 0

    return {
        "errors": errors,
        "infos": infos,
        "error_rate": error_rate
    }