import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
DATA_DIR = Path("./data")

def load_data():
    all_data = []
    files = sorted(DATA_DIR.glob("YT_data_*.json"))

    if not files:
        raise FileNotFoundError(f"No YT_data_*.json files found in {DATA_DIR}")

    for file_path in files:
        match = re.match(
            r"YT_data_(\d{4}-\d{2}-\d{2})\.json$", file_path.name
        )

        if not match:
            logger.warning(f"Skipping file with unexpected name: {file_path.name}")
            continue

        snapshot_date = match.group(1)
        logger.info(
            f"Processing {file_path.name} "
            f"with snapshot date {snapshot_date}"
        )

        with open(file_path, "r", encoding="utf-8") as file:
            videos = json.load(file)

        for video in videos:
            video["Snapshot_Date"] = snapshot_date
            all_data.append(video)

        logger.info(f"Loaded {len(videos)} videos from {file_path.name}")

    logger.info(f"Loaded {len(all_data)} total snapshot records")

    return all_data