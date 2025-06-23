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

    RETURN_TYPES = ("INT", "SEED_DATA", "STRING")
    RETURN_NAMES = ("seed", "seed_data", "log_path")
    FUNCTION = "track_seed"
    CATEGORY = "utils/seed_tracking"

    def track_seed(self, seed: int, node_id: str, notes: str = ""):
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

        # Create seed data dict for connecting to GlobalSeedTracker
        seed_data = {node_id: self.tracked_seeds[node_id]}

        return (seed, seed_data, log_path)

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

class GlobalSeedTracker:
    """
    A central node that collects and tracks seeds from connected Seed Tracker nodes
    and provides global seed management.
    """

    def __init__(self):
        self.output_dir = ensure_output_dir()
        self.session_id = generate_session_id()
        self.tracked_seeds = {}
        self.active = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "seed_data": ("SEED_DATA", {"forceInput": True}),
                "session_name": ("STRING", {"default": ""}),
                "show_debug": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "track_seeds"
    CATEGORY = "utils/seed_tracking"
    OUTPUT_NODE = True

    # Add optional debug output if requested
    OPTIONAL_OUTPUTS = [("log_path", "STRING")]

    def track_seeds(self, enabled: bool, seed_data=None, session_name: str = "", show_debug: bool = False):
        """Collect and track seeds from connected Seed Tracker nodes"""
        if not enabled:
            self.active = False
            return {"ui": {"text": "Seed tracking disabled"}} if show_debug else {}

        self.active = True

        # Use custom session name if provided, otherwise use generated ID
        session_id = session_name if session_name else self.session_id
        log_path = os.path.join(self.output_dir, f"global_seed_log_{session_id}.json")

        # Process incoming seed data if available
        if seed_data is not None:
            if isinstance(seed_data, dict):
                # Merge incoming seed data with our tracked seeds
                for node_id, seeds in seed_data.items():
                    if node_id not in self.tracked_seeds:
                        self.tracked_seeds[node_id] = []
                    if isinstance(seeds, list):
                        self.tracked_seeds[node_id].extend(seeds)
                    else:
                        self.tracked_seeds[node_id].append(seeds)

        # Prepare data for saving
        data = {
            "session_id": session_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Active" if self.active else "Inactive",
            "seeds": self.tracked_seeds,
            "total_seeds_tracked": sum(len(seeds) for seeds in self.tracked_seeds.values())
        }

        # Save the seed log
        save_json(data, log_path)

        # Return appropriate outputs based on show_debug flag
        if show_debug:
            return (log_path,)
        else:
            return {}

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