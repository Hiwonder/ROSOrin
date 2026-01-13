import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'large_models_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'large_models_examples'), glob(os.path.join('large_models_examples', '*.*'))),
        (os.path.join('share', package_name, 'large_models_examples', 'navigation_transport'), glob(os.path.join('large_models_examples', 'navigation_transport', '*.*'))),
        (os.path.join('share', package_name, 'large_models_examples', 'function_calling'), glob(os.path.join('large_models_examples', 'function_calling', '*.*'))),
        (os.path.join('share', package_name, 'large_models_examples', 'road_network'), glob(os.path.join('large_models_examples', 'road_network', '*.*'))),
        (os.path.join('share', package_name, 'large_models_examples', 'function_calling','road_network_llm'), glob(os.path.join('large_models_examples', 'function_calling', 'road_network_llm', '*.*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='2436210442@qq.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'navigation_controller = large_models_examples.navigation_controller:main',
            'llm_control_move = large_models_examples.llm_control_move:main',
            'llm_control_move_offline = large_models_examples.llm_control_move_offline:main',
            'llm_color_track = large_models_examples.llm_color_track:main',
            'llm_visual_patrol = large_models_examples.llm_visual_patrol:main',
            'vllm_with_camera = large_models_examples.vllm_with_camera:main',
            'vllm_track = large_models_examples.vllm_track:main',
            'vllm_navigation = large_models_examples.vllm_navigation:main',
            # function calling
            'llm_control = large_models_examples.function_calling.llm_control:main',
            # road network llm
            'road_network_navigator = large_models_examples.road_network.road_network_navigator:main',
            'nav2_execution_node = large_models_examples.road_network.nav2_execution_node:main',
            'road_network_tool = large_models_examples.function_calling.road_network_llm.road_network_tool:main',
        ],
    },
)
