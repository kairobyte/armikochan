import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import Joy
from rcl_interfaces.msg import SetParametersResult
import time

PARAM_NAME = 'current_recording_state'
RECORDING = 0

PATH = 'recording/pos.txt'

class JointStateRecorder(Node):
	def __init__(self):
		super().__init__('joint_state_recorder')

		self.out_file_name = PATH
		self.last_button_state = 0
		self.file_mode = 'w'

		self.declare_parameter(PARAM_NAME, RECORDING)
		self.add_on_set_parameters_callback(self.param_change_call)

		self.joint_state_sub = self.create_subscription(
			JointState,
			'/joint_states',
			self.joint_state_call,
			10
		)

		self.joy_sub = self.create_subscription(
			Joy,
			'/joy',
			self.joy_call,
			10
		)

	def joy_call(self, msg):
		button = msg.buttons[8]

		if button and not self.last_button_state:
			recording_state = self.get_parameter(PARAM_NAME).value
			self.toggle_recording_state(recording_state)
		self.last_button_state = button

	def toggle_recording_state(self, recording_state):
		new_state = 1 if not recording_state else 0
		self.set_parameters([Parameter(PARAM_NAME, Parameter.Type.INTEGER, new_state)])
		self.file_mode = 'w'
	
	def joint_state_call(self, msg):
		if self.get_parameter(PARAM_NAME).value:
			with open(self.out_file_name, self.file_mode) as out_file:
				# print(msg)
				out_file.write(str(msg.position)+'\n')
				time.sleep(0.01)
			self.file_mode = 'a'

	def param_change_call(self, params):
		for param in params:
			if param.name == PARAM_NAME and param.type_ == Parameter.Type.INTEGER:
				state = "Recording" if param.value else "Stopped recording"
				self.get_logger().info(f"{state}")
		return SetParametersResult(successful=True)

def main():
	try:
		rclpy.init()
		joint_state_recorder = JointStateRecorder()
		rclpy.spin(joint_state_recorder)
	except KeyboardInterrupt:
		pass
	finally:
		if rclpy.ok():
			joint_state_recorder.destroy_node()
			rclpy.shutdown()

if __name__=='__main__':
	main()