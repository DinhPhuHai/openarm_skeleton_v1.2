"""Contract tests for the prepared official robot descriptions."""

from pathlib import Path
import xml.etree.ElementTree as ET


PACKAGE = Path(__file__).resolve().parents[1]
FULL_URDF = PACKAGE / "urdf" / "openarm_skeleton_v1_2.urdf"
GAZEBO_URDF = PACKAGE / "urdf" / "openarm_skeleton_v1_2_base_demo.urdf"
LIFT_URDF = PACKAGE / "urdf" / "openarm_skeleton_v1_2_lift_demo.urdf"
ACTIVE_BASE_JOINTS = {
    "caster_joint_1",
    "caster_wheel_joint_1",
    "caster_joint_2",
    "caster_wheel_joint_2",
    "drive_joint_1",
    "drive_joint_2",
}
SKELETON_JOINTS = {
    f"skeleton_joint_{index}" for index in range(1, 6)
}


def _root(path):
    return ET.parse(path).getroot()


def test_full_description_has_expected_tree():
    root = _root(FULL_URDF)
    assert root.get("name") == "openarm_skeleton_v1.2"
    assert len(root.findall("./link")) == 37
    assert len(root.findall("./joint")) == 36
    assert root.find("./link[@name='base_footprint']") is not None
    assert root.find("./link[@name='cad_base_link']") is not None
    assert root.find("./link[@name='base_scan']") is not None


def test_mesh_uris_resolve_to_installed_package_assets():
    root = _root(FULL_URDF)
    prefix = "package://openarm_skeleton_v1_2_description/meshes/"
    meshes = root.findall(".//mesh")
    assert len(meshes) == 68
    for mesh in meshes:
        uri = mesh.get("filename", "")
        assert uri.startswith(prefix)
        assert (PACKAGE / "meshes" / uri.removeprefix(prefix)).is_file()


def test_base_demo_only_leaves_base_mechanics_movable():
    root = _root(GAZEBO_URDF)
    movable = {
        joint.get("name")
        for joint in root.findall("./joint")
        if joint.get("type") != "fixed"
    }
    assert movable == ACTIVE_BASE_JOINTS


def test_base_demo_has_diff_drive_contract():
    root = _root(GAZEBO_URDF)
    plugin = root.find(
        "./gazebo/plugin[@name='gz::sim::systems::DiffDrive']"
    )
    assert plugin is not None
    assert plugin.findtext("left_joint") == "drive_joint_1"
    assert plugin.findtext("right_joint") == "drive_joint_2"
    assert plugin.findtext("topic") == "/cmd_vel"
    assert float(plugin.findtext("wheel_separation")) == 0.45
    assert float(plugin.findtext("wheel_radius")) == 0.03810
    axes = {
        name: root.find(f"./joint[@name='{name}']/axis").get("xyz")
        for name in ("drive_joint_1", "drive_joint_2")
    }
    assert axes == {
        "drive_joint_1": "1 0 0",
        "drive_joint_2": "1 0 0",
    }


def test_base_demo_has_horizontal_navigation_lidar():
    root = _root(GAZEBO_URDF)
    joint = root.find("./joint[@name='base_scan_joint']")
    assert joint is not None
    assert joint.find("parent").get("link") == "base_link"
    assert joint.find("origin").get("xyz") == "0 0 0.34"
    assert joint.find("origin").get("rpy") == "0 0 0"
    sensor = root.find("./gazebo[@reference='base_scan']/sensor")
    assert sensor is not None
    assert sensor.get("type") == "gpu_lidar"
    assert sensor.findtext("topic") == "/scan"
    assert sensor.findtext("gz_frame_id") == "base_scan"
    assert float(sensor.findtext("lidar/range/min")) == 0.35
    assert float(sensor.findtext("lidar/range/max")) == 20.0


def test_base_demo_uses_primitive_collisions_only():
    root = _root(GAZEBO_URDF)
    collisions = root.findall("./link/collision")
    assert len(collisions) == 7
    assert not root.findall("./link/collision/geometry/mesh")


def test_lift_demo_exposes_only_base_and_five_skeleton_joints():
    root = _root(LIFT_URDF)
    movable = {
        joint.get("name")
        for joint in root.findall("./joint")
        if joint.get("type") != "fixed"
    }
    assert movable == ACTIVE_BASE_JOINTS | SKELETON_JOINTS

    assert (
        root.find("./joint[@name='drive_joint_1']/axis").get("xyz")
        == root.find("./joint[@name='drive_joint_2']/axis").get("xyz")
        == "1 0 0"
    )

    for name in SKELETON_JOINTS:
        joint = root.find(f"./joint[@name='{name}']")
        assert joint is not None
        assert joint.get("type") == "revolute"
        assert float(joint.find("limit").get("velocity")) == 0.5


def test_lift_demo_has_one_controller_per_skeleton_joint():
    root = _root(LIFT_URDF)
    controllers = root.findall(
        "./gazebo/plugin"
        "[@name='gz::sim::systems::JointPositionController']"
    )
    assert len(controllers) == 5
    assert {
        controller.findtext("joint_name") for controller in controllers
    } == SKELETON_JOINTS
