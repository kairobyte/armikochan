import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from sensor_msgs.msg import Joy
import time

FRAME_ID = "base_link"
joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7', 'tool_joint']

# default_pose = [0, 1.0, 0, 1.57, 0, 0.60, 0, 0]
default_pose = [0.02, 1.0, 0.05, 1.68, 0.0, 0.57, 0.08, 0.0]
# down_pose = [0, -0.6852, 0, 1.57, 0, 0.60, 0, 0]
down_pose = [0, -0.28, 0, 1.68, -0.1, 0.57, 0, 0]
# write_pose = [-1.09, -1.26, 0.72, 1.37, 2.29, 0.88, -0.15, 3.05]
write_pose = [0.0, 1.0, 0.01, 1.68, -0.104, 0.57, -0.08, 0.0]

class JointTrajectoryPublisher(Node):
	
	def __init__(self):
		super().__init__('joint_trajectory_controller')
		self.joint_traj_pub = self.create_publisher(JointTrajectory, "robotic_arm_controller/joint_trajectory", 10)
		self.joint_traj_pub
		
		self.joy_sub = self.create_subscription(Joy, "joy", self.joy_callback, 10)

		self.pose = "default"
		self.last_button_state = [0,0, 0]
		
	def joy_callback(self, msg):
		buttons = msg.buttons
		
		if buttons[0] and not buttons[0] == self.last_button_state[0]:
			if not self.pose == "default" and not self.pose=="down":
				self.pose = "default"
				self.timer_callback()
				time.sleep(1.5)
			self.pose = "down"
			self.timer_callback()
		elif buttons[1] and not buttons[1] == self.last_button_state[1]:
			if not self.pose == "default" and not self.pose == "write":
				self.pose = "default"
				self.timer_callback()
				time.sleep(1.5)
			self.pose = "write"
			self.timer_callback()
		elif buttons[2] and not buttons[2] == self.last_button_state[2]:
			self.pose = "default"
			self.timer_callback()
		self.last_button_state[0] = buttons[0]
		self.last_button_state[1] = buttons[1]
		self.last_button_state[2] = buttons[2]
			
	def timer_callback(self):

		joint_traj = JointTrajectory()
		joint_traj.header.frame_id = FRAME_ID
		joint_traj.header.stamp = self.get_clock().now().to_msg()
		joint_traj.joint_names = joints
		
		temp_point = JointTrajectoryPoint()
		if self.pose == "default":
			temp_point.positions = default_pose
			self.get_logger().info("Moving to start position")
		elif self.pose == "write":
			temp_point.positions = write_pose
			self.get_logger().info("Moving to drawing position")
		elif self.pose == "down":
			temp_point.positions = down_pose
			self.get_logger().info("Moving to down position")
		temp_point.time_from_start = Duration(sec=1, nanosec=0)
		
		joint_traj.points = [temp_point]
		
		self.joint_traj_pub.publish(joint_traj)
		self.get_logger().debug("Joint Trajectory Published")
		
	
def main():
	try: 
		rclpy.init()
		joint_trajectory_publisher = JointTrajectoryPublisher()		
		rclpy.spin(joint_trajectory_publisher)
	except KeyboardInterrupt:
		pass
	finally:	
		if rclpy.ok():
			joint_trajectory_publisher.destroy_node()
			rclpy.shutdown()

if __name__ == '__main__':
	main()

		