import rclpy
from rclpy.node import Node
from rcl_interfaces.srv import GetParameters
from sensor_msgs.msg import Joy
from geometry_msgs.msg import TwistStamped
from control_msgs.msg import JointJog

FRAME_ID = "base_link"

JOINT_JOG = 0
TWIST = 1

joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7', 'tool_joint']

class JointPublisher(Node):
    def __init__(self):
        super().__init__('servo_joint_publisher')

        # Joystick subscriber
        self.ps_listener_sub = self.create_subscription(Joy, 'joy', self.listener_call, 10)

        # Publishers
        self.joint_pub = self.create_publisher(JointJog, "servo_node/delta_joint_cmds", 10)

        # Create service client to get current command type
        self.cmd_type_sub = self.create_client(GetParameters, 'cmd_type_switcher/get_parameters')
        while not self.cmd_type_sub.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('cmd_type_switcher/get_parameters not available. waiting again...')

        self.req = GetParameters.Request()
        self.req.names = ['command_type']

        # Cache of current command type
        self.current_cmd_type = TWIST

        # Poll command type every second
        self.create_timer(0.5, self.update_command_type)

    def update_command_type(self):
        """Periodically check the command type from cmd_type_switcher node."""
        future = self.cmd_type_sub.call_async(self.req)
        future.add_done_callback(self.update_param_callback)
        
    def update_param_callback(self,future):
        if future.result() is not None:
            cmd_type = future.result().values[0].integer_value
            if cmd_type != self.current_cmd_type:
                self.current_cmd_type = cmd_type
                mode = "JOINT_JOG" if cmd_type == JOINT_JOG else "TWIST"
                # self.get_logger().debug(f"Switched to {mode} mode")
        else:
            self.get_logger().warn("Failed to fetch command type")

    def listener_call(self, msg):
        buttons = msg.buttons
        axes = msg.axes

        # Skip buttons/axes that are irrelevant
        buttons_check = all(a == 0 for i, a in enumerate(buttons) if i not in (0,1,2,3,5,7,8,9,10,11,12))
        axes_check = all(b == 0.0 for i, b in enumerate(axes) if i not in (2,5,6,7))
        all_zero = buttons_check and axes_check

        if all_zero:
            return

        if self.current_cmd_type == JOINT_JOG:
            req_joint = JointJog()
            req_joint.header.stamp = self.get_clock().now().to_msg()
            req_joint.header.frame_id = FRAME_ID
            req_joint.joint_names = joints
            req_joint.velocities = [-5*axes[0], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            self.joint_pub.publish(req_joint)
            self.get_logger().debug("JointJog command published")

def main():
    try:
        rclpy.init()
        servo_joint_publisher = JointPublisher()
        rclpy.spin(servo_joint_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            servo_joint_publisher.destroy_node()
            rclpy.shutdown()

if __name__ == "__main__":
    main()
