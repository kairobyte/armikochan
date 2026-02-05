import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import TwistStamped
from rcl_interfaces.srv import GetParameters

FRAME_ID = "base_link"
joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7', 'tool_joint']

JOINT_JOG = 0
TWIST = 1

class TwistPublisher(Node):

	def __init__(self):
		super().__init__('servo_twist_publisher')

		self.ps_listener_sub = self.create_subscription(Joy, 'joy', self.listener_call, 10)
		self.ps_listener_sub

		self.twist_pub = self.create_publisher(TwistStamped, "servo_node/delta_twist_cmds", 10)

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
		# rclpy.spin_until_future_complete(self, future)
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

		# Create a generator expression that ignores some indices of the 'axes' and 'buttons' list.
		# This is done because change in only few buttons on the PS4 needs to publish twist message
		buttons_check_generator = (a == 0 for i, a in enumerate(buttons) if i not in (0,1,2,3,5,7,8,9,10,11,12))
		axes_check_generator = (b == 0.0 for i, b in enumerate(axes) if i not in (2,5,6,7))

		all_zero = all(buttons_check_generator) and all(axes_check_generator)

		if all_zero:
			return 

		if self.current_cmd_type == TWIST:
			req_twist = TwistStamped()
			req_twist.header.stamp = self.get_clock().now().to_msg()
			req_twist.header.frame_id = FRAME_ID

			req_twist.twist.linear.x = axes[0]
			req_twist.twist.angular.x = axes[4]
			if buttons[4]:
				req_twist.twist.linear.z = axes[1]
				req_twist.twist.angular.y = axes[3]
			else:
				req_twist.twist.linear.y = -1 * axes[1]
				req_twist.twist.angular.z = -1 * axes[3]

			self.twist_pub.publish(req_twist)
			self.get_logger().debug(f"Twist Message Published")
		

def main():
	try:
		rclpy.init()
		twist_publisher = TwistPublisher()
		rclpy.spin(twist_publisher)
	except KeyboardInterrupt:
		pass
	finally:
		if rclpy.ok():
			twist_publisher.destroy_node()
			rclpy.shutdown()

			
if __name__ == "__main__":
	main()