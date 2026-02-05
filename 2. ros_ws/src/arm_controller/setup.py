import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'arm_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sushant',
    maintainer_email='081bel092.sushant@pcampus.edu.np',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
			"command_type_switcher = arm_controller.command_type_switcher:main",
            "joint_trajectory_controller = arm_controller.joint_trajectory_controller:main",
			"gripper_trajectory_controller = arm_controller.gripper_trajectory_controller:main",
            "joy_twist_publisher = arm_controller.joy_twist_publisher:main",
			"joy_joint_publisher = arm_controller.joy_joint_publisher:main",
			"joint_state_recorder = arm_controller.joint_state_recorder:main",
			"joint_state_player = arm_controller.joint_state_player:main",
			"ik_pub = arm_controller.ik_pub:main",
			"cam_controller = arm_controller.cam_controller:main",
        ],
    },
)
