import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from moveit_msgs.srv import ServoCommandType
from sensor_msgs.msg import Joy
from rcl_interfaces.msg import SetParametersResult

# =========================================================================
# Config Const
# =========================================================================
JOINT_JOG = 0
TWIST = 1

# =========================================================================
# ROS 2 Node
# =========================================================================
class CmdTypeSwitcher(Node):
	
	def __init__(self):
		super().__init__('cmd_type_switcher')

		self.switch_cmd_cli = self.create_client(ServoCommandType, 'servo_node/switch_command_type')
		while not self.switch_cmd_cli.wait_for_service(timeout_sec=1.0):
			self.get_logger().info("servo_node/switch_command_type not available, waiting again...")

		self.declare_parameter("command_type", TWIST)
		self.add_on_set_parameters_callback(self.param_change_call)

		self.joy_sub = self.create_subscription(Joy, 'joy', self.joy_call, 10)
		self.last_button_state = 0
		
		self.req = ServoCommandType.Request()

	def send_request(self, command_type):
		self.req.command_type = command_type
		return self.switch_cmd_cli.call_async(self.req)
	
	def param_change_call(self, params):
		result = SetParametersResult()
		for param in params: 
			if param.name == "command_type" and param.type_ == Parameter.Type.INTEGER:
				self.get_logger().info(f"command_type set to: {"TWIST" if param.value else "JOINT_JOG"}")
				self.send_request(param.value)
				result.successful = True
		return result
	
	def joy_call(self, msg):
		axes = msg.axes
		if axes[7] == -1 and not axes[7] == self.last_button_state:
			command_type = self.get_parameter('command_type').value
			self.toggle_cmd_type(command_type)
		self.last_button_state = axes[7]

	def toggle_cmd_type(self, cmd):
		new_cmd = JOINT_JOG if cmd == TWIST else TWIST
		self.set_parameters([Parameter('command_type', Parameter.Type.INTEGER, new_cmd)])

# =========================================================================
# Entry POint
# =========================================================================

def main():
	try:
		rclpy.init()
		cmd_type_switcher = CmdTypeSwitcher()
		cmd_type_switcher.toggle_cmd_type(JOINT_JOG)
		rclpy.spin(cmd_type_switcher)
	
	except KeyboardInterrupt:
		pass

	finally:
		if rclpy.ok():
			cmd_type_switcher.destroy_node()
			rclpy.shutdown()

if __name__ == '__main__':
	main()
