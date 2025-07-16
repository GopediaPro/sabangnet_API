import os
from pathlib import Path
from datetime import datetime

def write_log(message: str, log_name: str = "order_import.log") -> None:
    """
    Append a log message to the specified log file in the logs directory.
    Each message is prepended with a timestamp.
    The log file name will include a MMddhhmm timestamp to distinguish logs.
    """
    logs_dir = Path("./logs")
    logs_dir.mkdir(exist_ok=True)
    # Add MMddhhmm timestamp to log file name
    timestamp_for_filename = datetime.now().strftime("%m%d%H%M")
    if log_name.endswith(".log"):
        log_name = log_name[:-4] + f"_{timestamp_for_filename}.log"
    else:
        log_name = log_name + f"_{timestamp_for_filename}"
    log_path = logs_dir / log_name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n") 