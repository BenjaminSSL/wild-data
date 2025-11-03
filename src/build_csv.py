import json
import csv
from pathlib import Path
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import logging

logger = logging.getLogger(__name__)
 
 
MAX_WORKERS = 16
BATCH_SIZE = 5000
 

class ProgressTracker:
    """Track and display progress for file processing."""
    
    def __init__(self, total: int, update_interval: int = 20):
        self.total = total
        self.completed = 0
        self.update_interval = update_interval
        self.last_reported = 0
    
    def update(self, increment: int = 1) -> None:
        """Increment progress and print if threshold reached."""
        self.completed += increment
        
        # Print on interval or when complete
        if (self.completed - self.last_reported >= self.update_interval or 
            self.completed == self.total):
            self._print_progress()
            self.last_reported = self.completed
    
    def _print_progress(self) -> None:
        """Print current progress."""
        percentage = (self.completed / self.total) * 100
        print(f"Progress: {percentage:.1f}% ({self.completed}/{self.total} files)")
 
 
def _parse_datetime_from_filename(path: Path) -> str | None:
    """Extract datetime from filenames like 'cars_YYYYMMDD_HHMMSS.json'."""
    m = re.search(r"(\d{8}_\d{6})", path.name)
    if not m:
        return None
    s = m.group(1)
    try:
        dt = datetime.strptime(s, "%Y%m%d_%H%M%S")
        return dt.isoformat()
    except ValueError:
        return None
 
 
def _read_single_file(fp: Path) -> tuple[list[dict], str] | None:
    """Read a single JSON file and return data with filename."""
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, fp.name
    except Exception as exc:
        print(f"Warning: failed to read {fp}: {exc}")
        return None
 
 
def _build_csv_line(row: dict, fieldnames: list[str], delimiter: str = ',', quotechar: str = '"') -> str:
    """Manually build a CSV line - faster than csv.writer for simple cases."""
    values = []
    for field in fieldnames:
        val = row.get(field, '')
        val_str = str(val) if val is not None else ''
        # Only quote if necessary (contains delimiter, quote, or newline)
        if delimiter in val_str or quotechar in val_str or '\n' in val_str or '\r' in val_str:
            val_str = quotechar + val_str.replace(quotechar, quotechar + quotechar) + quotechar
        values.append(val_str)
    return delimiter.join(values) + '\n'

def main():
    logging.basicConfig(level=logging.INFO)
    args = argparse.ArgumentParser(description="Combine JSON files into a single CSV.")
    args.add_argument('--input', type=str, default="data/august/raw", help="Directory containing JSON files.")
    args.add_argument('--output', type=str, default="data/august/combined_output.csv", help="Output CSV file path.")
    args.add_argument('--max-workers', type=int, default=MAX_WORKERS, help="Maximum number of worker threads.")
    args.add_argument('--batch-size', type=int, default=BATCH_SIZE, help="Number of files to process in each batch.")
    args.add_argument('--progress', action='store_true', help="Show progress during processing.")
    args = args.parse_args()

    data_dir = Path(args.input)
    files = sorted(data_dir.glob("*.json"))
    
    total_files = len(files)
    output_path = Path(args.output)
    first_batch = True
    all_fieldnames = set()

    logger.info(f"Found {total_files} JSON files in {data_dir}")

    if args.progress:
        progress = ProgressTracker(total_files) 
    
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        for i in range(0, total_files, BATCH_SIZE):
            batch_files = files[i:i + BATCH_SIZE]
            batch_results = []
            # Read files in parallel
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_file = {executor.submit(_read_single_file, fp): fp for fp in batch_files}
                for future in as_completed(future_to_file):
                    result = future.result()
                    if result is not None:
                        batch_results.append(result)
                    if args.progress:
                        progress.update()
            # Process and collect rows
            if batch_results:
                batch_rows = []
                for result in batch_results:
                    data, filename = result
                    file_dt = _parse_datetime_from_filename(Path(filename))
                    for obj in data:
                        if file_dt:
                            obj["file_datetime"] = file_dt
                        all_fieldnames.update(obj.keys())
                        batch_rows.append(obj)
                if not batch_rows:
                    continue
                fieldnames = sorted(all_fieldnames)
                # Write header on first batch
                if first_batch:
                    outfile.write(','.join(fieldnames) + '\n')
                    first_batch = False
                # Build CSV content manually for speed
                lines = []
                for row in batch_rows:
                    lines.append(_build_csv_line(row, fieldnames))
                # Single write operation
                outfile.write(''.join(lines))
    logger.info(f"All data saved to {output_path}")
 
 
if __name__ == "__main__":
    main()