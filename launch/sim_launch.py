from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Nó 1: 
        Node(
            package='drone_control',
            executable='drone_node',  
            name='drone_simulator'
        ),
        # Nó 2: 
        Node(
            package='drone_control',
            executable='lidar_node',
            name='lidar_sensor'
        ),
        # Nó 3: 
        Node(
            package='drone_control',
            executable='comando_node',
            name='pygame_interface',
            output='screen',
            emulate_tty=True
        ),
    ])  