import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2 as cv
from cv_bridge import CvBridge


class CamPub(Node):
	def __init__(self):
		super().__init__('cam_publisher')

		self.cam_pub = self.create_publisher(Image, 'cam_publisher', 10)
		self.timer = self.create_timer(0.1, self.time_call)

		self.cap = cv.VideoCapture(2)
		self.bridge = CvBridge()


	def time_call(self):
		ret, frame = self.cap.read()
		if ret:
			ros_image = self.bridge.cv2_to_imgmsg(frame, "bgr8")
			self.cam_pub.publish(ros_image)
			self.get_logger().debug("Published Image")

def main():
	try:
		rclpy.init()
		cam_publisher = CamPub()
		cam_publisher.get_logger().info("Publishing Image")
		rclpy.spin(cam_publisher)
	except KeyboardInterrupt:
		pass
	finally:
		if rclpy.ok():
			cam_publisher.destroy_node()
			rclpy.shutdown()

if __name__ == '__main__':
	main()