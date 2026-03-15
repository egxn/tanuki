#!/usr/bin/env bash
# run_example_screenshot.sh — Generate a screenshot from a Tanuki DSL example.
#
# Usage:
#   ./blender_docs/examples/run_example_screenshot.sh \
#       blender_docs/examples/primitives_showcase.py \
#       blender_docs/images/primitives_showcase.png
#
# Prerequisites:
#   - `blender` must be in PATH
#   - Python venv with tanuki installed (or PYTHONPATH=src)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

DSL_SCRIPT="${1:?Usage: $0 <dsl_script.py> [output.png]}"
OUTPUT="${2:-blender_docs/images/$(basename "${DSL_SCRIPT%.py}").png}"

# Step 1: Run the DSL script to produce the _gen.py file
echo "==> Compiling DSL script: $DSL_SCRIPT"
PYTHONPATH="$REPO_ROOT/src" python "$DSL_SCRIPT"
GEN_SCRIPT="${DSL_SCRIPT%.py}_gen.py"

# If the gen file was created in cwd instead of beside the source
if [ ! -f "$GEN_SCRIPT" ]; then
    GEN_SCRIPT="$(basename "${DSL_SCRIPT%.py}")_gen.py"
fi

echo "==> Generated: $GEN_SCRIPT"

# Step 2: Run Blender headless to take the screenshot
echo "==> Launching Blender to render screenshot..."
blender --background --python "$SCRIPT_DIR/blender_screenshot.py" -- \
    --script "$GEN_SCRIPT" \
    --output "$OUTPUT" \
    --width 1280 \
    --height 720

echo "==> Done! Screenshot: $OUTPUT"
