#!/home/sushant/ros_ws/ignore/test_env/bin/python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Joy
import cv2 as cv
from cv_bridge import CvBridge
import mediapipe as mp
import time
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import TwistStamped
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter

# =========================================================================
# Config Const
# =========================================================================
AUTO_RUN = False  # Set True if you want to run this program directly without using PS4 controller

frame_id = "base_link"
joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7', 'tool_joint']
gripper_joints = ['grip_left_joint', 'grip_right_joint']

open_pos = [0.0, 0.0]
close_pos = [-0.04, 0.04]

class Position:
    def __init__(self, lx=0.0, ly=0.0):
        self.lx = lx
        self.ly = ly


# =========================================================================
# ROS 2 Node
# =========================================================================
class CamController(Node):

    def __init__(self):
        super().__init__('cam_controller')

        self.cam_sub = self.create_subscription(Image, 'cam_publisher', self.cam_call, 10)
        self.br = CvBridge()	

        self.cam_pub = self.create_publisher(Image, 'processed_cam_pub', 10)


        self.grip_pub = self.create_publisher(JointTrajectory, "gripper_controller/joint_trajectory", 10)
        self.twist_pub = self.create_publisher(TwistStamped, "servo_node/delta_twist_cmds", 10)

        self.joy_sub = self.create_subscription(Joy, 'joy', self.joy_call, 10)	
        self.last_button_state = 0

        if AUTO_RUN:
            self.declare_parameter("cam_controller_state", "working")
        else:
            self.declare_parameter("cam_controller_state", "idle")
        self.add_on_set_parameters_callback(self.param_change_call)

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(False, 1)
        self.mpDraw = mp.solutions.drawing_utils
        self.pTime = 0

    def ard_map(self, value, from_val, to_val):
        fromLow, fromHigh = from_val[0], from_val[1]
        toLow, toHigh = to_val[0], to_val[1]
        return float((value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow)

	# =====================================================================
	# read cam data -> change to publish the processed data
	# =====================================================================
    def cam_call(self, msg):
        self.get_logger().debug('Receiving video frame')

        frame = self.br.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        frame = cv.flip(frame, 1)
        imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)

        h,w,c = frame.shape
        centerX, centerY = w//2, h//2

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                x4 = y4 = x8 = y8 = 0
                cx4 = cy4 = cx8 = cy8 = 0

                for id, lm in enumerate(handLms.landmark):
                    if id==9:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv.circle(frame, (cx, cy), 5, (0, 255, 0), cv.FILLED)
                        cv.line(frame, (centerX, centerY), (cx, cy), (255, 255, 255), 2)
                        
                        x = self.ard_map(lm.x, [0, 1], [-1, 1])
                        y = self.ard_map(lm.y, [0, 1], [-1, 1])
                        cv.putText(frame, f'{x:.2f},{y:.2f}', (cx, cy), cv.FONT_HERSHEY_COMPLEX, 0.5, (0,255,0), 1)

                        # call joint_controller
                        pos = Position()
                        pos.lx = x
                        pos.ly = y
                        self.joint_controller(pos)

                    elif id == 4:
                        x4, y4 = lm.x, lm.y
                        cx4, cy4 = int(lm.x * w), int(lm.y * h)
                        cv.circle(frame, (cx4, cy4), 2, (0, 255, 0), cv.FILLED)
                    elif id == 8:
                        x8, y8 = lm.x, lm.y
                        cx8, cy8 = int(lm.x * w), int(lm.y * h)
                        cv.circle(frame, (cx8, cy8), 2, (0, 255, 0), cv.FILLED)

                 # Draw line between thumb & index tip
                cv.line(frame, (cx4, cy4), (cx8, cy8), (255, 255, 255), 1)

                dist = ((x4 - x8)**2 + (y4 - y8)**2)**0.5
                if dist < 0.04 :
                    cv.putText(frame, 'Closed', (cx4, cy4), cv.FONT_HERSHEY_COMPLEX, 0.7, (0,255,0), 2)
                    self.get_logger().debug("closed")
                    self.grip_controller('close')
                else:
                    cv.putText(frame, 'Opened', (cx4, cy4), cv.FONT_HERSHEY_COMPLEX, 0.7, (0,255,0), 2)
                    self.get_logger().debug("opened")
                    self.grip_controller('open')

        cTime = time.time()
        fps = 1 / (cTime - self.pTime) if cTime != self.pTime else 0
        self.pTime = cTime

        cv.circle(frame, (centerX, centerY), 4, (255, 0, 0), cv.FILLED)
        cv.putText(frame, f'FPS: {int(fps)}', (10, 40), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)

        ros_image = self.br.cv2_to_imgmsg(frame, "bgr8")
        self.cam_pub.publish(ros_image)
        self.get_logger().debug("Published Image")
        
        if AUTO_RUN:
            if self.get_parameter('cam_controller_state').value == "working":
                cv.imshow("Hand Tracking", frame)
                cv.waitKey(1)
            else:
                cv.destroyAllWindows()

    def joy_call(self, msg):
        button = msg.buttons[3] 
        if button and not button == self.last_button_state:
            cam_state = self.get_parameter("cam_controller_state").value
            self.toggle_cam_state(cam_state)
        self.last_button_state = button

    def param_change_call(self, params):
        result = SetParametersResult()
        for param in params:
            if param.name == "cam_controller_state" and param.type_ == Parameter.Type.STRING:
                self.get_logger().info(f"cam_controller_state set to: {param.value}")
                result.successful = True
        return result
    
    def toggle_cam_state(self, state):
        new_state = "working" if state == "idle" else "idle"
        self.set_parameters([Parameter("cam_controller_state", Parameter.Type.STRING, new_state)])

    def grip_controller(self, state):
        if self.get_parameter("cam_controller_state").value == "working":
            grip_traj = JointTrajectory()
            grip_traj.header.frame_id = frame_id
            grip_traj.header.stamp = self.get_clock().now().to_msg()
            grip_traj.joint_names = gripper_joints

            grip_point = JointTrajectoryPoint()
            grip_point.positions = close_pos if state == "close" else open_pos
            grip_point.time_from_start = Duration(sec=1)

            grip_traj.points = [grip_point]
        
            self.grip_pub.publish(grip_traj)
            self.get_logger().debug(f"Gripper {state}")

    def joint_controller(self, pos):
        if self.get_parameter("cam_controller_state").value == "working":
            joint_twist = TwistStamped()
            joint_twist.header.frame_id = frame_id
            joint_twist.header.stamp = self.get_clock().now().to_msg()

            joint_twist.twist.linear.x = 0.0
            joint_twist.twist.linear.y = 0.0
            joint_twist.twist.linear.z = 0.0

            joint_twist.twist.angular.x = -1 * pos.ly
            joint_twist.twist.angular.y = 0.0
            joint_twist.twist.angular.z = pos.lx

            self.twist_pub.publish(joint_twist)
            self.get_logger().debug(f'x={type(joint_twist.twist.linear.x)} y={joint_twist.twist.linear.x:.2f}')
            
def main():
    
    try:
        rclpy.init()
        cam_controller = CamController()
        rclpy.spin(cam_controller)
        
    except KeyboardInterrupt:
        pass
    
    finally:
        if rclpy.ok():
            cam_controller.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()