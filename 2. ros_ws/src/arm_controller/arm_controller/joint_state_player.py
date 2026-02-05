import threading
import time
import re
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from sensor_msgs.msg import Joy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from rcl_interfaces.msg import SetParametersResult
from builtin_interfaces.msg import Duration

PARAM_NAME = 'current_playing_state'
PLAYING = 0

ROBOT_FRAME_ID = "base_link"
GRIPPER_FRAME_ID = "link_7"

ROBOT_JOINTS = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7', 'tool_joint']
GRIPPER_JOINTS = ['grip_left_joint', 'grip_right_joint']

PATH = 'recording/pos.txt'

class JointStatePlayer(Node):
    def __init__(self):
        super().__init__('joint_state_player')

        self.in_file_name = PATH
        self.file_mode = 'r'
        self.last_button_state = 0
        self.play_thread = None

        self.declare_parameter(PARAM_NAME, PLAYING)
        self.add_on_set_parameters_callback(self.param_change_call)

        self.joint_traj_pub = self.create_publisher(JointTrajectory, "robotic_arm_controller/joint_trajectory", 10)
        self.gripper_traj_pub = self.create_publisher(JointTrajectory, "gripper_controller/joint_trajectory", 10)

        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_call, 10)

    def joy_call(self, msg):
        button = msg.buttons[9]
        if button and not self.last_button_state:
            playing_state = self.get_parameter(PARAM_NAME).value
            self.toggle_playing_state(playing_state)
        self.last_button_state = button

    def toggle_playing_state(self, playing_state):
        new_state = 1 if not playing_state else 0
        self.set_parameters([Parameter(PARAM_NAME, Parameter.Type.INTEGER, new_state)])
        if new_state == 1:
            # Start playback in a separate thread
            if self.play_thread is None or not self.play_thread.is_alive():
                self.play_thread = threading.Thread(target=self.play_file, daemon=True)
                self.play_thread.start()
        else:
            # If already playing, this flag change will make loop stop
            self.get_logger().debug("Playback interrupted!")

    def play_file(self):
        try:
            with open(self.in_file_name, self.file_mode) as in_file:
                count = 0
                for line in in_file:
                    # Check if playback was stopped mid-way
                    if not self.get_parameter(PARAM_NAME).value:
                        self.get_logger().debug("Playback stopped mid-way.")
                        break

                    lst = list(re.split(r'[\[\],]', line)[2:-1])
                    lst = [float(f) for f in lst if f.strip() != '']

                    joint_pos = lst[2:]
                    gripper_pos = lst[:2]

                    # Publish arm
                    joint_traj = JointTrajectory()
                    joint_traj.header.frame_id = ROBOT_FRAME_ID
                    joint_traj.header.stamp = self.get_clock().now().to_msg()
                    joint_traj.joint_names = ROBOT_JOINTS
                    point = JointTrajectoryPoint()
                    point.positions = joint_pos
                    point.time_from_start = Duration(sec=1, nanosec=0)
                    joint_traj.points = [point]
                    self.joint_traj_pub.publish(joint_traj)

                    # Publish gripper
                    gripper_traj = JointTrajectory()
                    gripper_traj.header.frame_id = GRIPPER_FRAME_ID
                    gripper_traj.header.stamp = self.get_clock().now().to_msg()
                    gripper_traj.joint_names = GRIPPER_JOINTS
                    gpoint = JointTrajectoryPoint()
                    gpoint.positions = gripper_pos
                    gpoint.time_from_start = Duration(sec=1, nanosec=0)
                    gripper_traj.points = [gpoint]
                    self.gripper_traj_pub.publish(gripper_traj)

                    count += 1
                    time.sleep(0.02)

                self.get_logger().debug(f"Playback complete. {count} poses published.")

                if self.get_parameter(PARAM_NAME).value:
                    self.toggle_playing_state(1)

        except FileNotFoundError:
            self.get_logger().error("File not found.")
        except Exception as e:
            self.get_logger().error(f"Error: {str(e)}")


    def param_change_call(self, params):
        for param in params:
            if param.name == PARAM_NAME and param.type_ == Parameter.Type.INTEGER:
                state = "Playing" if param.value else "Stopped playing"
                self.get_logger().info(f"{state}")
        return SetParametersResult(successful=True)


def main():
    try:
        rclpy.init()
        node = JointStatePlayer()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
