# ComfyUI Seed Tracker

A custom node extension for ComfyUI that tracks and logs random seeds used throughout your image generation workflows.

## Features

- Track individual seeds from specific nodes
- Track batches of seeds from batch processing
- Global seed tracking mode to monitor all seeds in a workflow
- Export seed logs in different formats (JSON, CSV, TXT)
- Organize seeds by session ID for easy reference
- Add custom notes to tracked seeds

## Installation

1. Navigate to your ComfyUI custom_nodes directory:
   ```
   cd ComfyUI/custom_nodes/
   ```

2. Clone this repository:
   ```
   git clone https://github.com/angelcookies/comfyui-seed-tracker.git
   ```

   Alternatively, download and extract the ZIP file to your custom_nodes directory.

3. Restart ComfyUI

## Usage

After installation, you'll find the following nodes in the "utils/seed_tracking" category:

### Seed Tracker Node

Connect this node to track seeds from individual nodes.

Inputs:
- `seed`: The seed value to track
- `node_id`: A unique identifier for the node (helps with organization)
- `notes`: Optional notes to add context to the tracked seed

Outputs:
- `seed`: The same seed passed through (for convenience in workflows)
- `log_path`: Path to the JSON log file

### Seed Tracker Batch Node

Designed for batch processing, this node can track multiple seeds at once.

Inputs:
- `seeds`: A batch of seed values to track
- `node_id`: A unique identifier for the source
- `notes`: Optional notes

Outputs:
- `seeds`: The same seeds passed through
- `log_path`: Path to the JSON log file

### Global Seed Tracker Node

A standalone node that creates a session log file.

Inputs:
- `enabled`: Toggle tracking on/off
- `include_metadata`: Include workflow metadata in logs
- `session_name`: Optional custom session name

Outputs:
- `log_path`: Path to the session log file

### Seed Exporter Node

Export tracked seeds in different formats.

Inputs:
- `session_id`: The session ID to export
- `format`: Output format (json, csv, txt)

Outputs:
- `export_path`: Path to the exported file

## Log Files

All seed logs are stored in your ComfyUI output directory under a `seed_logs` folder. Each session creates a unique log file with timestamp-based naming.

## Example Workflow

1. Add a "Global Seed Tracker" node at the beginning of your workflow
2. Connect "Seed Tracker" nodes to any KSampler or other nodes where you want to track seeds
3. When you want to reference seeds later, use the "Seed Exporter" node to export them in your preferred format

## Advanced Integration

For advanced users who want to automatically track all seeds without manually connecting nodes, you can modify the ComfyUI server code to hook into the execution system. This requires deeper integration with the ComfyUI API and is beyond the scope of this basic extension.

## Future Features

- Automatic seed detection without manual node connections
- Web UI for browsing and searching captured seeds
- Integration with prompt history
- Thumbnail generation for associated images

## Credits

- Development assisted by Claude AI from Anthropic
- Special thanks to the ComfyUI community

## License

MIT License