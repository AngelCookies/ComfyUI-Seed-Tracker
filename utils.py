# File: seed_tracker/utils.py

import os
import json
import datetime
import csv
import folder_paths
from typing import Dict, Any, List


def generate_session_id() -> str:
    """Generate a unique session ID based on current timestamp"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_output_dir() -> str:
    """Ensure the output directory exists and return its path"""
    output_dir = os.path.join(folder_paths.get_output_directory(), "seed_logs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file with proper formatting"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file"""
    if not os.path.exists(file_path):
        return {}

    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def find_seed_logs(session_id: str = None) -> List[str]:
    """Find all seed log files, optionally filtered by session ID"""
    output_dir = ensure_output_dir()
    log_files = []

    for file in os.listdir(output_dir):
        if file.endswith('.json') and 'seed_log' in file:
            if session_id is None or session_id in file:
                log_files.append(os.path.join(output_dir, file))

    return log_files


def export_to_csv(data: Dict[str, Any], file_path: str) -> None:
    """Export seed data to CSV format"""
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Node ID', 'Seed', 'Timestamp', 'Notes'])

        if 'seeds' in data:
            for node_id, seed_list in data['seeds'].items():
                for seed_entry in seed_list:
                    writer.writerow([
                        node_id,
                        seed_entry.get('seed', ''),
                        seed_entry.get('timestamp', ''),
                        seed_entry.get('notes', '')
                    ])


def get_comfyui_version() -> str:
    """Get the current ComfyUI version if available"""
    try:
        import comfy
        return getattr(comfy, "__version__", "unknown")
    except:
        return "unknown"