"""Launch Isaac Sim 5.0, the OpenArm ROS contract, SLAM/Nav2, and RViz."""

import os
from pathlib import Path

from ament_index_python.packages import (
    get_package_prefix,
    get_package_share_directory,
)
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    ExecuteProcess,
    IncludeLaunchDescription,
    LogInfo,
    OpaqueFunction,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import Node


def _is_true(value):
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _isaac_environment():
    """Use Isaac's Python 3.11 ROS libraries, not system Jazzy Python 3.12."""
    environment = dict(os.environ)
    for name in (
        "AMENT_PREFIX_PATH",
        "CMAKE_PREFIX_PATH",
        "COLCON_PREFIX_PATH",
        "PYTHONHOME",
        "PYTHONPATH",
        "ROS_DISTRO",
        "ROS_PYTHON_VERSION",
        "ROS_VERSION",
    ):
        environment.pop(name, None)
    inherited_libraries = environment.get("LD_LIBRARY_PATH", "")
    environment["LD_LIBRARY_PATH"] = os.pathsep.join(
        entry
        for entry in inherited_libraries.split(os.pathsep)
        if entry
        and "/opt/ros/" not in entry
        and "/install/" not in entry
    )
    environment["RMW_IMPLEMENTATION"] = "rmw_fastrtps_cpp"
    return environment


def _shutdown_on_unexpected_exit(action, label):
    def _on_exit(event, context):
        if context.is_shutdown:
            return []
        return [
            EmitEvent(
                event=Shutdown(
                    reason=f"{label} exited with code {event.returncode}"
                )
            )
        ]

    return RegisterEventHandler(
        OnProcessExit(target_action=action, on_exit=_on_exit)
    )


def _launch_setup(context):
    isaac_prefix = Path(
        get_package_prefix("openarm_skeleton_v1_2_isaac")
    )
    description_share = Path(
        get_package_share_directory("openarm_skeleton_v1_2_description")
    )
    gazebo_share = Path(
        get_package_share_directory("openarm_skeleton_v1_2_gazebo")
    )
    navigation_share = Path(
        get_package_share_directory("openarm_skeleton_v1_2_navigation")
    )
    nav2_share = Path(get_package_share_directory("nav2_bringup"))

    start_isaac = _is_true(
        LaunchConfiguration("start_isaac").perform(context)
    )
    headless = _is_true(LaunchConfiguration("headless").perform(context))
    slam = _is_true(LaunchConfiguration("slam").perform(context))
    map_path = LaunchConfiguration("map").perform(context).strip()
    if not slam and (not map_path or not Path(map_path).is_file()):
        raise RuntimeError(
            "Localization mode requires map:=/absolute/path/to/map.yaml"
        )

    source_urdf = (
        description_share
        / "urdf"
        / "openarm_skeleton_v1_2_base_demo.urdf"
    )
    mesh_directory = description_share / "meshes"
    runner = (
        isaac_prefix
        / "lib"
        / "openarm_skeleton_v1_2_isaac"
        / "openarm_isaac_sim.py"
    )
    for path, label in (
        (source_urdf, "base-demo URDF"),
        (mesh_directory, "mesh directory"),
        (runner, "installed Isaac runner"),
    ):
        if not path.exists():
            raise RuntimeError(f"{label} not found: {path}")

    simulator = None
    actions = []
    if start_isaac:
        isaac_sim_path = Path(
            LaunchConfiguration("isaac_sim_path")
            .perform(context)
            .strip()
        ).expanduser()
        isaac_python = isaac_sim_path / "python.sh"
        if not isaac_sim_path.is_absolute() or not isaac_python.is_file():
            raise RuntimeError(
                "Isaac Sim python.sh not found. Set "
                "isaac_sim_path:=/absolute/path/to/isaac-sim-5.0.0"
            )
        command = [
            str(isaac_python),
            str(runner),
            "--source-urdf",
            str(source_urdf),
            "--mesh-dir",
            str(mesh_directory),
            "--max-frames",
            LaunchConfiguration("max_frames").perform(context),
            "--lidar-config",
            LaunchConfiguration("lidar_config").perform(context),
        ]
        if headless:
            command.append("--headless")
        simulator = ExecuteProcess(
            cmd=command,
            output="screen",
            shell=False,
            env=_isaac_environment(),
        )
        actions.extend(
            [
                LogInfo(
                    msg=(
                        "Starting the light OpenArm Isaac scene; Nav2 waits "
                        "for /clock, /scan, /odom, /joint_states and TF."
                    )
                ),
                _shutdown_on_unexpected_exit(simulator, "Isaac Sim"),
                simulator,
            ]
        )
    else:
        actions.append(
            LogInfo(
                msg=(
                    "Using an already-running Isaac Sim process; waiting "
                    "for its ROS 2 runtime contract."
                )
            )
        )

    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")
    params_file = LaunchConfiguration("params_file")
    robot_description = source_urdf.read_text(encoding="utf-8")
    state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="official_isaac_robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": use_sim_time,
            }
        ],
    )
    watchdog = Node(
        package="openarm_skeleton_v1_2_gazebo",
        executable="cmd_vel_watchdog.py",
        name="official_isaac_cmd_vel_watchdog",
        output="screen",
        parameters=[str(gazebo_share / "config" / "cmd_vel_watchdog.yaml")],
    )
    readiness = Node(
        package="openarm_skeleton_v1_2_isaac",
        executable="check_isaac_runtime.py",
        name="openarm_isaac_startup_check",
        output="screen",
        arguments=[
            "--timeout",
            LaunchConfiguration("startup_timeout").perform(context),
        ],
    )

    slam_localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(nav2_share / "launch" / "slam_launch.py")
        ),
        condition=IfCondition(LaunchConfiguration("slam")),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "autostart": autostart,
            "params_file": params_file,
            "use_respawn": "false",
        }.items(),
    )
    map_localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(nav2_share / "launch" / "localization_launch.py")
        ),
        condition=UnlessCondition(LaunchConfiguration("slam")),
        launch_arguments={
            "map": LaunchConfiguration("map"),
            "use_sim_time": use_sim_time,
            "autostart": autostart,
            "params_file": params_file,
            "use_composition": "false",
            "use_respawn": "false",
        }.items(),
    )
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(navigation_share / "launch" / "navigation.launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "autostart": autostart,
            "params_file": params_file,
        }.items(),
    )
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="isaac_nav2_rviz",
        output="screen",
        arguments=[
            "-d",
            str(navigation_share / "config" / "nav2_openarm_view.rviz"),
        ],
        parameters=[{"use_sim_time": use_sim_time}],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
    )
    nav_actions = [
        LogInfo(msg="Isaac ROS contract passed; starting SLAM/Nav2."),
        slam_localization,
        map_localization,
        navigation,
        TimerAction(period=2.0, actions=[rviz]),
    ]

    def _after_readiness(event, _context):
        if event.returncode == 0:
            return nav_actions
        return [
            EmitEvent(
                event=Shutdown(
                    reason=(
                        "Isaac ROS topics/TF did not become ready; "
                        f"checker exited with code {event.returncode}"
                    )
                )
            )
        ]

    actions.extend(
        [
            state_publisher,
            watchdog,
            _shutdown_on_unexpected_exit(
                state_publisher, "Robot state publisher"
            ),
            _shutdown_on_unexpected_exit(
                watchdog, "Base command watchdog"
            ),
            RegisterEventHandler(
                OnProcessExit(
                    target_action=readiness,
                    on_exit=_after_readiness,
                )
            ),
            readiness,
        ]
    )
    return actions


def generate_launch_description():
    navigation_share = Path(
        get_package_share_directory("openarm_skeleton_v1_2_navigation")
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("start_isaac", default_value="true"),
            DeclareLaunchArgument(
                "isaac_sim_path",
                default_value=EnvironmentVariable(
                    "ISAAC_SIM_PATH", default_value=""
                ),
            ),
            DeclareLaunchArgument("headless", default_value="false"),
            DeclareLaunchArgument("max_frames", default_value="0"),
            DeclareLaunchArgument(
                "lidar_config", default_value="Example_Rotary_2D"
            ),
            DeclareLaunchArgument("startup_timeout", default_value="600.0"),
            DeclareLaunchArgument("slam", default_value="true"),
            DeclareLaunchArgument("map", default_value=""),
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("autostart", default_value="true"),
            DeclareLaunchArgument(
                "params_file",
                default_value=str(
                    navigation_share / "config" / "nav2_params.yaml"
                ),
            ),
            OpaqueFunction(function=_launch_setup),
        ]
    )
