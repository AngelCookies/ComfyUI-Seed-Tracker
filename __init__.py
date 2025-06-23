from .node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from .utils import get_comfyui_version

# Version information
__version__ = "1.0.0"

# Register custom data type for seed tracking
CUSTOM_NODE_TYPE_MAPPINGS = {
    "SEED_DATA": {"base_type": "DICT", "display_name": "Seed Data"}
}

# ComfyUI manager metadata
NODE_CLASS_MAPPINGS = NODE_CLASS_MAPPINGS
NODE_DISPLAY_NAME_MAPPINGS = NODE_DISPLAY_NAME_MAPPINGS

# Add version information for ComfyUI extension manager
VERSION = __version__

# ComfyUI version compatibility
COMFYUI_REQUIRED_VERSION = "Tested with ComfyUI [ComfyUI_00_stable]"
COMFYUI_CURRENT_VERSION = get_comfyui_version()

print(f"ComfyUI Seed Tracker v{__version__} initialized")
print(f"Running on ComfyUI version: {COMFYUI_CURRENT_VERSION}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'VERSION', 'CUSTOM_NODE_TYPE_MAPPINGS']