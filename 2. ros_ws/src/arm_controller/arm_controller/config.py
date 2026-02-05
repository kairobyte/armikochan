FRAME_ID = "base_link"
ROBOT_JOINTS = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7', 'tool_joint']
GRIPPER_JOINTS = ['grip_left_joint', 'grip_right_joint']

open_pos = [0.0, 0.0]
close_pos = [-0.04, 0.04]

SVG_FILE = "svg/workspace.svg"

SCALE_FACTOR = 0.001       # Converts SVG px → meters
PEN_DOWN_Z = 0.07          # Z height when drawing
PEN_UP_Z = 0.15            # Z height when moving
ST_WIDTH = 1.0

# Orientation of end effector in quaternion
default_orient = [
    0.7068251814624406,
    0.7073873723632136,
    0.0011261755880557509,
    0.0
]

# File to store the positions for recording mode
PATH = 'recording/pos.txt'

default_pose = [0, 1.0, 0, 1.57, 0, 0.60, 0, 0]
down_pose = [0, -0.6852, 0, 1.57, 0, 0.60, 0, 0]
write_pose = [-1.09, -1.26, 0.72, 1.37, 2.29, 0.88, -0.15, 3.05]

# Command Type
JOINT = 0
TWIST = 1
