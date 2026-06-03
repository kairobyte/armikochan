# ============================================================================
# File: setup_assistant.launch.py
# Auto-added section markers and high-level comments
# ============================================================================

# ====== Imports ======
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_setup_assistant_launch


# Function: generate_launch_description
# ====== Functions ======
def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("arm_description", package_name="arm_moveit").to_moveit_configs()
    return generate_setup_assistant_launch(moveit_config)
