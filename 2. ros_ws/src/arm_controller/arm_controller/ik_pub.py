import time
import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from sensor_msgs.msg import Joy

import xml.etree.ElementTree as ET
from svg.path import parse_path
import matplotlib.pyplot as plt

# ===============================================================
# Configuration Constants
# ===============================================================
AUTO_RUN = False
SVG_FILE = "svg/workspace.svg"

SCALE_FACTOR = 0.001       # Converts SVG px → meters
PEN_DOWN_Z = 0.07          # Z height when drawing
PEN_UP_Z = 0.15            # Z height when moving
ST_WIDTH = 1.0

NODE_NAME = "ik_cmd_pub"

# End-effector quaternion orientation
default_orient = [
    0.7068251814624406,
    0.7073873723632136,
    0.0011261755880557509,
    0.0
]

# ===============================================================
# SVG Parsing Utilities
# ===============================================================

def extract_coordinates_from_svg(svg_file):
    """
    Parse SVG and extract all drawing coordinates.
    Supports path, circle, rectangle, and polygon.
    """
    try:
        tree = ET.parse(svg_file)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"[ERROR] File '{svg_file}' not found.")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to parse SVG: {e}")
        return []

    ns = {'svg': 'http://www.w3.org/2000/svg'}
    coordinates = []

    # ------------------- PATHS -------------------
    for path_elem in root.findall('.//svg:path', ns):
        path_data = path_elem.get('d')
        if not path_data:
            continue

        try:
            path = parse_path(path_data)
            for segment in path:
                segment_type = segment.__class__.__name__

                # Each path segment includes start & end points
                start = (segment.start.real, segment.start.imag)
                end = (segment.end.real, segment.end.imag)

                coordinates.append({
                    'type': segment_type,
                    'points': [start, end]
                })

        except Exception as e:
            print(f"[WARNING] Failed to parse path: {e}")
            continue

    # ------------------- CIRCLES -------------------
    for circle in root.findall('.//svg:circle', ns):
        cx = float(circle.get('cx', 0))
        cy = float(circle.get('cy', 0))
        r = float(circle.get('r', 0))
        coordinates.append({
            'type': 'Circle',
            'center': (cx, cy),
            'radius': r
        })

    # ------------------- RECTANGLES -------------------
    for rect in root.findall('.//svg:rect', ns):
        x = float(rect.get('x', 0))
        y = float(rect.get('y', 0))
        width = float(rect.get('width', 0))
        height = float(rect.get('height', 0))

        coordinates.append({
            'type': 'Rectangle',
            'points': [
                (x, y),
                (x + width, y),
                (x + width, y + height),
                (x, y + height),
                (x, y)
            ]
        })

    # ------------------- POLYGONS -------------------
    for polygon in root.findall('.//svg:polygon', ns):
        points = polygon.get('points', '').strip()
        if points:
            point_list = []
            for point in points.split():
                x, y = map(float, point.split(','))
                point_list.append((x, y))
            coordinates.append({
                'type': 'Polygon',
                'points': point_list
            })

    return coordinates


# ===============================================================
# ROS 2 Node
# ===============================================================

class IkPublisher(Node):
    def __init__(self):
        super().__init__(NODE_NAME)
        self.get_logger().info("IK Command Publisher initialized.")

        # ROS interfaces
        self.ik_pub_ = self.create_publisher(Pose, NODE_NAME, 10)
        self.joy_sub_ = self.create_subscription(Joy, 'joy', self.joy_callback, 10)

        # Internal state
        self.point_index = 0
        self.last_axis_state = 0

        # Auto run mode
        if AUTO_RUN:
            self.create_timer(1.0, self.start_drawing)

    # ===========================================================
    # Joystick Control
    # ===========================================================
    def joy_callback(self, msg):
        axis = msg.axes[7]
        if axis == 1.0 and axis != self.last_axis_state:
            self.start_drawing()
        self.last_axis_state = axis

    # ===========================================================
    # Main Drawing Logic
    # ===========================================================
    def start_drawing(self):
        self.get_logger().info("Starting SVG drawing...")
        coordinates = extract_coordinates_from_svg(SVG_FILE)
        draw_points = []

        fig, ax = plt.subplots()

        for item in coordinates:
            if item['type'] == 'Rectangle':
                # x_vals = [p[0] * SCALE_FACTOR - ST_WIDTH for p in item['points']]
                # y_vals = [-p[1] * SCALE_FACTOR + ST_WIDTH for p in item['points']]
                # ax.plot(x_vals, y_vals, 'm-')
                # for (x, y) in item['points']:
                #     draw_points.append([x * SCALE_FACTOR, -y * SCALE_FACTOR, PEN_DOWN_Z])
                continue

            elif item['type'] in ['Circle']:
                cx = item['center'][0] * SCALE_FACTOR - ST_WIDTH
                cy = -item['center'][1] * SCALE_FACTOR + ST_WIDTH
                r = item['radius'] * SCALE_FACTOR
                circle_patch = plt.Circle((cx, cy), r, fill=False, color='b')
                ax.add_patch(circle_patch)
                continue

            else:
                # Handle Line / CubicBezier / QuadraticBezier
                pts = item['points']
                for i, (a, b) in enumerate(pts):
                    tx = a * SCALE_FACTOR - ST_WIDTH
                    ty = -b * SCALE_FACTOR + ST_WIDTH
                    tz = PEN_DOWN_Z if item['type'] != 'Move' else PEN_UP_Z
                    draw_points.append([tx, ty, tz])
                    ax.plot(tx, ty, 'ko', markersize=2)

        # Visualize extracted points
        plt.title("Extracted SVG Paths")
        plt.xlabel("X (m)")
        plt.ylabel("Y (m)")
        # plt.plot((0,0), 'o')
        plt.grid(True)
        plt.axis('equal')
        if AUTO_RUN:
            plt.show(block=True)

        # Publish poses sequentially
        self.publish_poses(draw_points)

        self.get_logger().info("Drawing complete.")
        if AUTO_RUN:
            self.destroy_node()
            sys.exit()

    # ===========================================================
    # Pose Publisher
    # ===========================================================
    def publish_poses(self, points):
        for i, (x, y, z) in enumerate(points):
            pose = Pose()
            pose.position.x = x
            pose.position.y = y
            pose.position.z = z
            pose.orientation.w = default_orient[0]
            pose.orientation.x = default_orient[1]
            pose.orientation.y = default_orient[2]
            pose.orientation.z = default_orient[3]

            self.ik_pub_.publish(pose)
            self.get_logger().info(f"Published {i+1}/{len(points)}: x={x:.3f}, y={y:.3f}, z={z:.3f}")
            time.sleep(0.3)  # Adjust for smoother drawing


# ===============================================================
# Entry Point
# ===============================================================
def main():
    rclpy.init()
    node = IkPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
