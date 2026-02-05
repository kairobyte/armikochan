from setuptools import find_packages, setup

package_name = 'rsp_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sushant',
    maintainer_email='mail@sushant.uk',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
			'serial_controller = rsp_controller.serial_controller:main',
			'cam_publisher = rsp_controller.cam_publisher:main',
        ],
    },
)
