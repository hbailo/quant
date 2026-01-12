import argparse
from datetime import datetime, timezone
from pathlib import Path
import requests
from tqdm import tqdm

KLINES_ENDPOINT = "https://api.binance.com/api/v3/klines"

DEFAULT_START_TIME = "2019-01-01T00:00:00+00:00"
DEFAULT_END_TIME = datetime.now(timezone.utc).isoformat()
INTERVAL = "1m"
LIMIT = 1000
INTERVAL_STEP = 60000
TIME_STEP = LIMIT * INTERVAL_STEP

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def posix_ms_to_filename(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp // 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H-%MZ")

def validate_arguments():
    parser = argparse.ArgumentParser(description="Fetch Binance klines for a given symbol and interval.")
    
    parser.add_argument("symbol",
                        type=str,
                        help="Trading symbol, e.g., BTCUSDT")

    parser.add_argument("--start-time",
                        "-s",
                        type=str,
                        help=f"Start time in ISO 8601 format (UTC). Defaults to {DEFAULT_START_TIME}.",
                        default=DEFAULT_START_TIME)

    parser.add_argument("--end-time",
                        "-e",
                        type=str,
                        help="End time in ISO 8601 format (UTC). Defaults to the current time.",
                        default=DEFAULT_END_TIME)

    args = parser.parse_args()
    
    symbol = args.symbol.upper()

    start_time = None
    
    try:
        start_time = int(datetime.fromisoformat(args.start_time).timestamp() * 1000)
    except ValueError:
        parser.error(f"Start time must be in ISO 8601 format (UTC), e.g., {DEFAULT_START_TIME}")

    end_time = None
    
    try:
        end_time = int(datetime.fromisoformat(args.end_time).timestamp() * 1000)
    except ValueError:
        parser.error(f"End time must be in ISO 8601 format (UTC), e.g., {DEFAULT_END_TIME}")


    if start_time >= end_time:
        parser.error("Start time must be earlier than end time.")
        
    return symbol, start_time, end_time

def collect_klines(symbol: str, start_time: int, end_time: int):
    params = {
        "symbol"    : symbol,
        "interval"  : INTERVAL,
        "limit"     : LIMIT,
        "startTime" : start_time,
        "endTime"   : end_time
    }

    data_dir = BASE_DIR / "data" / "raw" / "binance" / "spot" / symbol.lower() / "klines"
    data_dir.mkdir(parents=True, exist_ok=True)

    total_requests = (end_time - start_time) // TIME_STEP + 1
    
    with tqdm(total=total_requests, desc="Collecting", unit="batch") as pbar:
        current_start = start_time
        
        while start_time < end_time:
            r = requests.get(KLINES_ENDPOINT, params=params)
        
            r.raise_for_status()

            filename = data_dir / f"{posix_ms_to_filename(start_time)}.json"
        
            with open(filename, "w", encoding="utf-8") as f:
                f.write(r.text)

            start_time = start_time + TIME_STEP
            params["startTime"] = start_time

            # Progress bar update
            pbar.update(1)
            pbar.set_postfix({"last_file": filename.name})
            
def main():
    symbol, start_time, end_time = validate_arguments()
        
    collect_klines(symbol, start_time, end_time)
            
if __name__ == "__main__":
    main()
