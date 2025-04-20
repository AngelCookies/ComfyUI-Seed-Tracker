import os
import datetime
from typing import Dict, List, Any, Tuple, Union
import folder_paths
from .utils import save_json, generate_session_id, ensure_output_dir

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


class SeedTrackerBatch:
    """
Tracks multiple seeds at once, useful for batch processing
workflows in ComfyUI.
    """
    def __init__(self):
        self.tracker = SeedTracker()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seeds": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "forceInput": True}),
                "node_id": ("STRING", {"default": "unknown_node"}),
            },
            "optional": {
                "notes": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("seeds", "log_path")
    FUNCTION = "track_seeds"
    CATEGORY = "utils/seed_tracking"

    def track_seeds(self, seeds: Union[int, List[int]], node_id: str, notes: str = "") -> Tuple[Union[int, List[int]], str]:
        """Track multiple seeds from a batch"""
        log_path = ""

        # Handle both single seeds and lists of seeds
        if isinstance(seeds, list):
            for idx, seed in enumerate(seeds):
                seed_note = f"{notes} (batch item {idx})"
                _, log_path = self.tracker.track_seed(seed, f"{node_id}_{idx}", seed_note)
        else:
            _, log_path = self.tracker.track_seed(seeds, node_id, notes)

        return (seeds, log_path)


class GlobalSeedTracker:
    """
A node that hooks into the workflow and attempts to track all seeds
across the entire ComfyUI workflow.
    """
    def __init__(self):
        self.all_seeds = {}
        self.output_dir = ensure_output_dir()
        self.session_id = generate_session_id()

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
            return ("Tracking disabled",)

        # In a real implementation, this would hook into ComfyUI's event system
        # For now, we'll just create a placeholder log file
        session_id = session_name if session_name else self.session_id
        log_path = os.path.join(self.output_dir, f"global_seed_log_{session_id}.json")

        data = {
            "session_id": session_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "Global seed tracking activated",
            "include_metadata": include_metadata
        }

        save_json(data, log_path)
        return (log_path,)


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
        # Implementation would read from existing seed logs
        # and export them in the requested format

        export_path = os.path.join(self.output_dir, f"seed_export_{session_id}.{format}")

        # Placeholder - in a real implementation, we would read and convert actual data
        data = {
            "message": f"Seeds exported in {format} format",
            "session_id": session_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        save_json(data, export_path)
        return (export_path,)


# Node mapping for ComfyUI
NODE_CLASS_MAPPINGS = {
    "SeedTracker": SeedTracker,
    "SeedTrackerBatch": SeedTrackerBatch,
    "GlobalSeedTracker": GlobalSeedTracker,
    "SeedExporter": SeedExporter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedTracker": "Seed Tracker",
    "SeedTrackerBatch": "Seed Tracker (Batch)",
    "GlobalSeedTracker": "Global Seed Tracker",
    "SeedExporter": "Seed Exporter"
}