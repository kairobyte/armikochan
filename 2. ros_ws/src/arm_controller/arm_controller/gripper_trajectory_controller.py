import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from sensor_msgs.msg import Joy
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter

FRAME_ID = "tool_link"
JOINTS = ['grip_left_joint', 'grip_right_joint']

OPEN_POS = [0.0, 0.0]
CLOSE_POS = [-0.04, 0.04]

class GripperTrajectoryController(Node):
    def __init__(self):
        super().__init__('gripper_trajectory_controller')
        self.joint_traj_pub = self.create_publisher(JointTrajectory, "gripper_controller/joint_trajectory", 10)
        self.joy_sub = self.create_subscription(Joy, "joy", self.joy_callback, 10)

        self.declare_parameter("gripper_state_param", "OPENED")
        self.add_on_set_parameters_callback(self.paramChangeCallback)
        self.last_button_state = 0

    def paramChangeCallback(self, params):
        result = SetParametersResult()
        for param in params:
            if param.name == "gripper_state_param" and param.type_ == Parameter.Type.STRING:
                self.get_logger().debug(f"gripper_state_param set to: {param.value}")
                result.successful = True
        return result

    def joy_callback(self, msg):
        if msg.buttons[7] and not self.last_button_state:
            gripper_state = self.get_parameter("gripper_state_param").value
            self.toggle_gripper(gripper_state)
        self.last_button_state = msg.buttons[7]

    def toggle_gripper(self, state):
        new_state = "CLOSED" if state == "OPENED" else "OPENED"
        self.set_parameters([Parameter("gripper_state_param", Parameter.Type.STRING, new_state)])

        joint_traj = JointTrajectory()
        joint_traj.header.frame_id = FRAME_ID
        joint_traj.header.stamp = self.get_clock().now().to_msg()
        joint_traj.joint_names = JOINTS

        point = JointTrajectoryPoint()
        point.positions = CLOSE_POS if new_state == "CLOSED" else OPEN_POS
        point.time_from_start = Duration(sec=1)

        joint_traj.points = [point]
        self.joint_traj_pub.publish(joint_traj)
        self.get_logger().info(f"Gripper {new_state.lower()}")

def main():
    try:
        rclpy.init()
        gripper_trajectory_controller = GripperTrajectoryController()
        rclpy.spin(gripper_trajectory_controller)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            gripper_trajectory_controller.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
