import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from sensor_msgs.msg import Joy
import serial


# Hardware / motor parameters
REDUCTION_RATIO = 4.1538
STEPS_PER_REV = 400
STAGES = [2, 3, 2, 2, 2, 2, 1, 1]


class SerialController(Node):
    def __init__(self):
        super().__init__('serial_controller')

        # Subscriptions
        self.joint_state_sub = self.create_subscription(
            JointState,
            'joint_states',
            self.serial_publisher,
            10
        )

        self.joy_sub = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10
        )

        # Serial port
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
            self.get_logger().info("Serial port opened successfully")
        except serial.SerialException as e:
            self.get_logger().error(f"Failed to open serial port: {e}")
            raise

        # State tracking
        self.last_joint_steps = [0] * 8
        self.last_gripper_positions = [0.0, 0.0]
        self.last_sent_gripper_cmd = None      # '0' or '1'
        self.gripper_hysteresis_band = 0.015   # adjust based on your gripper jitter/noise

        # Typical gripper position ranges (ADJUST THESE TO MATCH YOUR SYSTEM)
        # Many grippers use: 0.0 = closed, positive = open
        self.gripper_open_threshold = 0.02     # above this → considered open
        self.gripper_close_threshold = 0.005   # below this → considered closed

    def joy_callback(self, msg: Joy):
        # Placeholder — implement joystick gripper control here if needed
        # Example: button 1 (index 0) to toggle gripper
        pass

    def serial_publisher(self, msg: JointState):
        if len(msg.position) != 10:
            self.get_logger().error(f"Expected 10 joint positions, got {len(msg.position)}")
            return

        # Extract gripper (first two joints) and arm joints
        gripper_pos = msg.position[:2]          # [left_finger, right_finger] or similar
        arm_pos = msg.position[2:10]            # 8 arm joints

        # Compute motor steps for the 8 arm joints
        steps = []
        for i in range(8):
            angle_rad = arm_pos[i]
            reduced_steps = angle_rad * (REDUCTION_RATIO ** STAGES[i]) * (STEPS_PER_REV / (2 * math.pi))
            step_int = int(round(reduced_steps))
            steps.append(step_int)

        # =============================================
        #          GRIPPER DECISION LOGIC
        # =============================================
        # Use average of both gripper joints (more robust against small asymmetries)
        avg_gripper = gripper_pos[1]

        # Determine desired state with hysteresis
        if self.last_sent_gripper_cmd is None:
            # First time — simple threshold
            new_cmd = '0' if avg_gripper >= self.gripper_open_threshold else '1'
        else:
            # Hysteresis: only change state if we cross a wider band
            if self.last_sent_gripper_cmd == '0':  # currently open
                if avg_gripper < (self.gripper_open_threshold - self.gripper_hysteresis_band):
                    new_cmd = '1'  # close
                else:
                    new_cmd = '0'
            else:  # currently closed
                if avg_gripper > (self.gripper_close_threshold + self.gripper_hysteresis_band):
                    new_cmd = '0'  # open
                else:
                    new_cmd = '1'

        # =============================================
        #          CHANGE DETECTION
        # =============================================
        joints_changed = steps != self.last_joint_steps
        gripper_cmd_changed = new_cmd != self.last_sent_gripper_cmd

        # For gripper position comparison we round to reduce float noise sensitivity
        rounded_current_gripper = [round(x, 5) for x in gripper_pos]
        rounded_last_gripper = [round(x, 5) for x in self.last_gripper_positions]
        gripper_pos_changed = rounded_current_gripper != rounded_last_gripper

        if not (joints_changed or gripper_cmd_changed or gripper_pos_changed):
            return  # nothing meaningful changed → skip send

        # Build command string
        joint_str = ','.join(map(str, steps))
        command = f"{joint_str},{new_cmd}\n"
        
        # Logging (very helpful for debugging random behavior)
        self.get_logger().info(
            f"Arm steps: {steps} | "
            f"Gripper pos: [{gripper_pos[0]:.4f}, {gripper_pos[1]:.4f}] "
            f"(avg: {avg_gripper:.4f}) | "
            f"cmd: {new_cmd} (was {self.last_sent_gripper_cmd}) | "
            f"sending: {command.strip()}"
        )

        # Send to Arduino / controller
        try:
            self.ser.write(command.encode('utf-8'))
            response = self.ser.readline().decode('utf-8').strip()
            if response:
                self.get_logger().debug(f"Arduino response: {response}")
        except serial.SerialException as e:
            self.get_logger().error(f"Serial write/read failed: {e}")

        # Update stored state
        self.last_joint_steps = steps[:]
        self.last_gripper_positions = gripper_pos[:]
        self.last_sent_gripper_cmd = new_cmd

    def destroy_node(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            self.get_logger().info("Serial port closed")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = SerialController()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if node is not None:
            node.get_logger().error(f"Unexpected error: {e}")
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()