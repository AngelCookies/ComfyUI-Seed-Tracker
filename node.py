# File: seed_tracker/node.py

import os
import datetime
from typing import Dict, Any, Tuple, Union, List
import folder_paths
from .utils import save_json, generate_session_id, ensure_output_dir, load_json, export_to_csv


class SeedTracker:
    """
    A node that tracks individual seeds used in the workflow
    and saves them to a log file.
    """

    def __init__(self):
        self.output_dir = ensure_output_dir()
        self.tracked_seeds = {}
        self.session_id = generate_session_id()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "node_id": ("STRING", {"default": "unknown_node"}),
            },
            "optional": {
                "notes": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("seed", "log_path")
    FUNCTION = "track_seed"
    CATEGORY = "utils/seed_tracking"
    OUTPUT_NODE = True

    def track_seed(self, seed: int, node_id: str, notes: str = "") -> Tuple[int, str]:
        """Track a seed value and associate it with a node ID"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if node_id not in self.tracked_seeds:
            self.tracked_seeds[node_id] = []

        seed_entry = {
            "seed": seed,
            "timestamp": timestamp,
            "notes": notes
        }

        self.tracked_seeds[node_id].append(seed_entry)

        # Save to log file
        log_path = self.save_seed_log()

        return (seed, log_path)

    def save_seed_log(self) -> str:
        """Save the tracked seeds to a JSON file"""
        log_filename = f"seed_log_{self.session_id}.json"
        log_path = os.path.join(self.output_dir, log_filename)

        data = {
            "session_id": self.session_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "seeds": self.tracked_seeds
        }

        save_json(data, log_path)
        return log_path


class GlobalSeedTracker:
    """
    A node that hooks into the workflow and attempts to track all seeds
    across the entire ComfyUI workflow.
    """

    def __init__(self):
        self.all_seeds = {}
        self.output_dir = ensure_output_dir()
        self.session_id = generate_session_id()
        self.active = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
                "include_metadata": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "session_name": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("log_path",)
    FUNCTION = "start_tracking"
    CATEGORY = "utils/seed_tracking"
    OUTPUT_NODE = True

    def start_tracking(self, enabled: bool, include_metadata: bool, session_name: str = "") -> Tuple[str]:
        """Start tracking all seeds in the workflow"""
        if not enabled:
            self.active = False
            return ("Tracking disabled",)

        self.active = True

        # Create a session log file
        session_id = session_name if session_name else self.session_id
        log_path = os.path.join(self.output_dir, f"global_seed_log_{session_id}.json")

        # Try to hook into ComfyUI's seed generation
        try:
            # This is a placeholder - in a real implementation we would
            # need to find a way to hook into ComfyUI's execution system
            # One approach would be to monkey patch the functions that generate seeds
            from comfy.samplers import prepare_sampling
            original_prepare_sampling = prepare_sampling

            def patched_prepare_sampling(*args, **kwargs):
                result = original_prepare_sampling(*args, **kwargs)
                if self.active and 'noise' in kwargs:
                    # Record the seed
                    self._record_seed(kwargs.get('seed', 0), 'sampler', 'Auto-captured by GlobalSeedTracker')
                return result

            # This is commented out because it would need to be tested carefully
            # prepare_sampling = patched_prepare_sampling

        except Exception as e:
            # If we can't hook into the system, just note that in the log
            pass

        data = {
            "session_id": session_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Active" if self.active else "Inactive",
            "include_metadata": include_metadata,
            "message": "Global seed tracking activated - using manual tracking mode"
        }

        save_json(data, log_path)
        return (log_path,)

    def _record_seed(self, seed, source, notes):
        """Internal method to record a captured seed"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if source not in self.all_seeds:
            self.all_seeds[source] = []

        self.all_seeds[source].append({
            "seed": seed,
            "timestamp": timestamp,
            "notes": notes
        })

        # Update the log file
        log_path = os.path.join(self.output_dir, f"global_seed_log_{self.session_id}.json")

        data = {
            "session_id": self.session_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Active",
            "seeds": self.all_seeds
        }

        save_json(data, log_path)


class SeedExporter:
    """
    Exports all tracked seeds from a session to various formats
    like JSON, CSV, or text.
    """

    def __init__(self):
        self.output_dir = ensure_output_dir()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "session_id": ("STRING", {"default": ""}),
                "format": (["json", "csv", "txt"], {"default": "json"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("export_path",)
    FUNCTION = "export_seeds"
    CATEGORY = "utils/seed_tracking"

    def export_seeds(self, session_id: str, format: str) -> Tuple[str]:
        """Export seeds from a session in the specified format"""
        # Find seed logs for the specified session
        output_dir = self.output_dir
        log_files = []

        for file in os.listdir(output_dir):
            if file.endswith('.json') and 'seed_log' in file:
                if not session_id or session_id in file:
                    log_files.append(os.path.join(output_dir, file))

        if not log_files:
            # No logs found
            export_path = os.path.join(output_dir, f"no_seeds_found_{session_id}.{format}")
            with open(export_path, 'w') as f:
                f.write(f"No seed logs found for session {session_id}")
            return (export_path,)

        # Combine data from all log files
        combined_data = {
            "session_id": session_id,
            "export_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "seeds": {}
        }

        for log_file in log_files:
            data = load_json(log_file)
            if "seeds" in data:
                for node, seeds in data["seeds"].items():
                    if node not in combined_data["seeds"]:
                        combined_data["seeds"][node] = []
                    combined_data["seeds"][node].extend(seeds)

        # Export in requested format
        if format == "json":
            export_path = os.path.join(output_dir, f"seed_export_{session_id}.json")
            save_json(combined_data, export_path)

        elif format == "csv":
            export_path = os.path.join(output_dir, f"seed_export_{session_id}.csv")
            export_to_csv(combined_data, export_path)

        elif format == "txt":
            export_path = os.path.join(output_dir, f"seed_export_{session_id}.txt")
            with open(export_path, 'w') as f:
                f.write(f"Seed Export for Session: {session_id}\n")
                f.write(f"Generated on: {combined_data['export_date']}\n\n")

                for node, seeds in combined_data["seeds"].items():
                    f.write(f"Node: {node}\n")
                    f.write("-" * 40 + "\n")

                    for idx, seed_data in enumerate(seeds):
                        f.write(f"  Seed #{idx + 1}: {seed_data['seed']}\n")
                        f.write(f"  Time: {seed_data['timestamp']}\n")
                        if seed_data.get('notes'):
                            f.write(f"  Notes: {seed_data['notes']}\n")
                        f.write("\n")

                    f.write("\n")

        else:
            # Unsupported format
            export_path = os.path.join(output_dir, f"unsupported_format_{session_id}.txt")
            with open(export_path, 'w') as f:
                f.write(f"Unsupported export format: {format}")

        return (export_path,)


# Node mapping for ComfyUI
NODE_CLASS_MAPPINGS = {
    "SeedTracker": SeedTracker,
    "GlobalSeedTracker": GlobalSeedTracker,
    "SeedExporter": SeedExporter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedTracker": "Seed Tracker",
    "GlobalSeedTracker": "Global Seed Tracker",
    "SeedExporter": "Seed Exporter"
}