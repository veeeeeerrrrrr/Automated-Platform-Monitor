from config import LOG_FILE

def analyze_logs():
    error_count = 0
    info_count = 0

    with open(LOG_FILE, "r") as file:
        for line in file:
            if "ERROR" in line:
                error_count += 1
            elif "INFO" in line:
                info_count += 1

    return error_count, info_count

def anomaly_score():
    error_count, info_count = analyze_logs()

    if error_count > 5:
        return "High Anomaly Risk"
    elif error_count > 2:
        return "Moderate Anomaly Risk"
    else:
        return "Low Risk"