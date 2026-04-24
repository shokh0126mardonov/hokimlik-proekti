# apps/analytics/utils.py

def format_duration(td):
    if not td:
        return None

    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60

    return f"{days}d {hours}h {minutes}m"