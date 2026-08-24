# Historical Humble runtime acceptance report — 2026-08-06

> Kết quả dưới đây là baseline Humble/Fortress trước migration, không phải bằng
> chứng runtime cho Jazzy/Harmonic.

## Scope

Workspace under test:

```text
/home/hai/openarm_skeleton_v1.2_ws
```

No package from `/home/hai/sim-workspace` was sourced or used at runtime.

## Build and source contracts

Commands:

```bash
cd /home/hai/openarm_skeleton_v1.2_ws
./scripts/build_workspace.sh
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

Result:

```text
2 packages built
18 tests
0 errors
0 failures
0 skipped
```

The tests cover the 36-link/35-joint model, 68 mesh references, base and
skeleton-lift movable-joint allowlists, Gazebo plugins, local hotel assets,
transport partition validation, route bounds, wall-time command watchdog and
semantic lift profiles.

## Hotel route runtime

Command:

```bash
ROS_DOMAIN_ID=92 ./scripts/run_hotel_demo.sh \
  headless:=true linear_speed:=0.30
```

Gazebo transport partition: `openarm_sim_98490`.

Result:

```text
Spawned entity 'openarm_skeleton_hotel' successfully
Segment 1 PASS: measured 3.966 m
Segment 2 PASS: final heading error +1.95 deg
Segment 3 PASS: measured 1.966 m
Segment 4 PASS: final heading error -1.95 deg
Segment 5 PASS: measured 2.965 m
INDOOR ROUTE PASS:
  measured_linear=8.897 m
  net_displacement=7.267 m
  final_pose=(6.996, 1.967, -0.0 deg)
```

No duplicate-spawn, additional-clock or backward-time warning appeared.

## Skeleton-lift runtime

Command:

```bash
ROS_DOMAIN_ID=93 ./scripts/run_skeleton_demo.sh \
  headless:=true demo_duration:=4.0
```

Result:

```text
Spawned entity 'openarm_skeleton' successfully
Reached HIGH: max error=0.0000 rad
measured=[-0.524, 1.047, -1.047, 1.047, -0.524]
Skeleton lift demo PASS
```

This is simulation-only evidence. It does not validate mechanical limits,
actuator load, balance, coupling, homing or hardware safety.

## Source handoff archive

Artifact:

```text
dist/openarm_skeleton_v1.2_ws-source-20260806.tar.gz
dist/openarm_skeleton_v1.2_ws-source-20260806.tar.gz.sha256
```

Archive acceptance:

```text
Checksum: PASS
Generated/build/git/cache content: absent
STL assets: 34
Fresh extraction path:
  /tmp/openarm-handoff-test.0yb56U/openarm_skeleton_v1.2_ws
Fresh build: 2 packages PASS
Fresh tests: 18 tests, 0 errors, 0 failures, 0 skipped
Fresh runtime route_scale=0.25:
  INDOOR ROUTE PASS
  measured_linear=2.148 m
  net_displacement=1.764 m
  final_pose=(1.701, 0.468, -0.0 deg)
```

This verifies that source assets and runtime resolution do not depend on the
original `/home/hai/openarm_skeleton_v1.2_ws/build` or `install` trees.

## Jazzy/Harmonic runtime acceptance — 2026-08-19

Host: Ubuntu 24.04 x86_64, ROS 2 Jazzy, Gazebo Sim 8.11.0 (Harmonic).
Workspace không source hoặc dùng package từ `/home/hai/sim-workspace`.

### Build và automated tests

```bash
source /opt/ros/jazzy/setup.bash
python3 -B tools/prepare_model.py
colcon build --symlink-install
source install/setup.bash
colcon test --event-handlers console_cohesion+
colcon test-result --verbose
```

Kết quả cuối:

```text
Build: 3 packages finished
Tests: 25 tests, 0 errors, 0 failures, 0 skipped
```

### Gazebo hotel route

```bash
ROS_DOMAIN_ID=150 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ./scripts/run_hotel_demo.sh \
  headless:=true route_scale:=0.25 linear_speed:=0.30
```

```text
Segment 1 PASS: measured 0.966 m
Segment 2 PASS: final heading error +1.94 deg
Segment 3 PASS: measured 0.466 m
Segment 4 PASS: final heading error -1.95 deg
Segment 5 PASS: measured 0.715 m
INDOOR ROUTE PASS:
  measured_linear=2.147 m
  net_displacement=1.763 m
  final_pose=(1.700, 0.468, 0.0 deg)
```

### Skeleton-lift simulation

```bash
ROS_DOMAIN_ID=151 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ./scripts/run_skeleton_demo.sh \
  headless:=true demo_duration:=4.0
```

```text
Reached HIGH: max error=0.0000 rad
measured=[-0.524, 1.047, -1.047, 1.047, -0.524]
Skeleton lift demo PASS
```

Đây chỉ là bằng chứng simulation; không xác nhận an toàn cơ khí/hardware.

### Nav2 + SLAM acceptance

```bash
ROS_DOMAIN_ID=149 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ./scripts/run_nav2_sim.sh headless:=true use_rviz:=false

# terminal thứ hai, cùng ROS_DOMAIN_ID
ros2 run openarm_skeleton_v1_2_navigation check_nav2_goal.py \
  --goal-distance 0.60 --min-motion 0.25 --goal-timeout 90
```

Đã xác nhận:

```text
/scan: base_scan, 720 rays, about 10 Hz, nearest scene return 2.191 m
TF: map -> odom -> base_footprint -> base_link -> base_scan
SLAM Toolbox: active
Nav2 lifecycle nodes: active
Local and global costmaps: publishing
Watchdog: forwarded command, then zeroed it after 0.528 s wall time
Nav2: Goal succeeded
PASS: action_status=4, goal_distance=0.600 m,
      odom_motion=0.577 m, delta_x=0.575 m, delta_y=-0.037 m
```

Lidar ban đầu tự nhìn thấy mesh robot vì GPU lidar dùng visual geometry. Profile
simulation hiện đặt `base_scan` ở `0 0 0.34` trong `base_link` và dùng minimum
range 0,35 m. Đây là simulation self-filter, không phải extrinsic hardware.

### Dependency note

Nav2, SLAM Toolbox, `ros_gz`, build tools và toàn bộ runtime trên đã có đủ.
`rosdep check` còn báo thiếu riêng `ros-jazzy-joint-state-publisher-gui`, chỉ
dùng cho display launch có GUI. Cài bằng:

```bash
sudo apt install ros-jazzy-joint-state-publisher-gui
```

Script `scripts/install_jazzy_dependencies.sh` đã bao gồm package này cho lần
cài mới.

### Snap VS Code GUI environment fix — 2026-08-19

Lần chạy GUI từ integrated terminal của Snap VS Code ban đầu dừng sớm:

```text
rviz2: exit code 127
/snap/core20/current/lib/x86_64-linux-gnu/libpthread.so.0:
  undefined symbol: __libc_pthread_init, version GLIBC_PRIVATE
```

`planner_server` sau đó nhận SIGINT giữa lúc configure và thoát `-6`; đây là
hậu quả của toàn launch shutdown, không phải lỗi planner configuration.
Các wrapper `run_nav2_sim.sh`, `run_hotel_demo.sh` và
`run_skeleton_demo.sh` hiện source `clean_snap_gui_environment.bash` để bỏ
GTK/GIO path core20 khi phát hiện Snap VS Code. Critical-process shutdown cũng
chỉ emit một shutdown event.

Acceptance sau sửa bằng đúng GUI wrapper:

```text
Gazebo GUI: running
RViz2: running, OpenGL 4.6
planner_server: lifecycle state active
Nav2 managed nodes: active
Ctrl+C: no "Cannot shutdown a ROS adapter that is not running"
Automated tests: 25 tests, 0 errors, 0 failures, 0 skipped
```

### Gazebo full-reset guard — 2026-08-19

Khi nhấn full Reset trong Gazebo, live inspection cho thấy simulation time về
0, model `openarm_skeleton_hotel` biến mất khỏi entity list, `/odom` và `/scan`
ngừng cập nhật. Respawn robot phục hồi sensor nhưng Nav2/SLAM báo TF cũ vì
`/clock` đã nhảy lùi, nên session đó không còn hợp lệ.

Hotel/Nav2 hiện dùng `config/hotel_nav_gui.config`: camera khởi động gần vị trí
robot và plugin `WorldControl` (chứa full Reset) bị loại khỏi GUI. RViz dùng
`config/nav2_openarm_view.rviz`, bật sẵn `RobotModel`. Cách reset được hỗ trợ
là `Ctrl+C` và chạy lại toàn launch.

Acceptance GUI bằng `./scripts/run_nav2_sim.sh` sau sửa:

```text
Gazebo model list: openarm_skeleton_hotel present
Gazebo view: robot visible on the blue hotel_start_zone
Gazebo WorldControl / full-reset button: absent
/odom: about 50 Hz
/scan: about 10 Hz
planner_server: active
controller_server: active
RViz: workspace config loaded, RobotModel enabled
Automated tests: 25 tests, 0 errors, 0 failures, 0 skipped
```

### Differential-drive axis và SLAM correction — 2026-08-19

Nguyên nhân map bị xoay/chồng và robot đi sai Nav2 goal là hai trục bánh chủ
động trong URDF SolidWorks bị mirror: `drive_joint_1` là `1 0 0` nhưng
`drive_joint_2` là `-1 0 0`. Gazebo DiffDrive tự đặt dấu vận tốc trái/phải khi
quay, nên giữ hai trục ngược dấu làm chuyển động thẳng và quay của chassis bị
đổi cho nhau. Odometry vẫn báo command mong muốn vì nó do cùng plugin tạo ra;
do đó acceptance chỉ đọc `/odom` trước đây có thể PASS giả.

`tools/prepare_model.py` hiện chuẩn hóa cả hai drive axis thành `1 0 0` cho hai
profile simulation. Test description khóa contract này để lỗi không quay lại.
URDF tham chiếu gốc từ SolidWorks không bị sửa.

Đo trước khi sửa:

```text
command angular.z=+0.30 rad/s trong 4 s:
  odom yaw=+0.720 rad; Gazebo chassis yaw=0.000 rad; chassis trượt 0.162 m
command linear.x=+0.20 m/s trong 4 s:
  Gazebo chassis tiến 0.003 m nhưng quay 2.981 rad
```

Đo lại sau khi sửa, đọc độc lập cả `/odom` và pose vật lý Gazebo:

```text
command linear.x=+0.20 m/s trong 4 s:
  Gazebo chassis tiến 0.53822 m, yaw=0.000 rad
  odom tiến 0.53820 m, yaw xấp xỉ 0
command angular.z=+0.30 rad/s trong 4 s:
  Gazebo chassis quay 0.51298 rad, trôi 0.00024 m
  odom quay xấp xỉ 0.490 rad
```

Nav2/SLAM được khởi động lại từ session sạch. Goal thẳng 0,60 m trả
`SUCCEEDED`, `/odom` đo 0,438 m và Gazebo đo 0,434 m. Goal thứ hai có cả tịnh
tiến và quay cũng `SUCCEEDED`; pose tương đối cuối từ `/odom` là khoảng
`(0.657, 0.393, 0.897 rad)`, còn Gazebo là
`(0.633, 0.398, 0.926 rad)`. Map lưu sau các lần quay có tường đơn, sắc nét,
không còn hình cánh hoa do các scan bị ghép ở góc sai.

Hotel route được chạy lại với `route_scale:=0.25`. Script báo:

```text
INDOOR ROUTE PASS:
  measured_linear=2.147 m
  final_pose=(1.700, 0.468, 0.0 deg)
```

Pose vật lý Gazebo cuối là `(-3.332, -3.015, 0.032 rad)` từ vị trí spawn
`(-5.000, -3.500, 0.000 rad)`, tức dịch chuyển tương đối xấp xỉ
`(1.668, 0.485, 0.032 rad)` và phù hợp với odometry của route.

Lưu ý: SLAM Toolbox tạo occupancy grid 2D từ mặt phẳng quét lidar, không tái
tạo màu/texture hay toàn bộ hình học 3D của Gazebo. Vùng sau vật cản hoặc chưa
được quét vẫn là unknown; điều cần kiểm tra là hình học tường ổn định và không
bị xoay lặp khi robot đổi hướng.

### Straight-path refinement — 2026-08-19

Chassis được kiểm tra riêng với command thẳng và không tự drift. Phần đi cong
còn lại đến từ global plan: lidar simulation cũ có range 8 m, trong khi hướng
trước tại hotel spawn không có vật trả về trong 8 m. SLAM map vì vậy để một
wedge lớn phía trước là unknown. NavFn được phép đi qua unknown nhưng ưu tiên
các ô free đã quan sát, nên tạo đường vòng chữ S dù goal nằm thẳng trước robot.

Đã thay đổi:

- lidar simulation, SLAM Toolbox và AMCL dùng range 20 m, đủ bao phủ lobby;
- hai obstacle layer raytrace đến 20 m và coi laser `+inf` là phép đo clearing;
- planner goal tolerance giảm từ 0,50 m xuống 0,10 m;
- behavior tree mới gọi `SimpleSmoother` sau mỗi lần NavFn replan;
- goal tolerance giảm còn 0,08 m và yaw tolerance còn 0,05 rad;
- `check_nav2_goal.py` đo cross-track error và FAIL nếu lớn hơn 0,05 m trong
  bài test hành lang trống.

So sánh cùng goal thẳng 1,20 m từ hotel spawn:

```text
Trước refinement:
  odom delta=(1.063, -0.122) m
  lateral deviation khoảng 0.122 m

Sau mở rộng lidar, trước path smoothing:
  odom delta=(1.003, +0.015) m
  lateral deviation khoảng 0.015 m

Sau refinement hoàn chỉnh:
  PASS: odom_motion=1.124 m, along_track=1.124 m,
        cross_track=0.006 m, max_cross_track=0.050 m
  Gazebo ground truth relative=(1.123, 0.0047, -0.0447 rad)
```

`smoother_server` log xác nhận nhận và xử lý path ở mỗi lần replan. Map khởi
tạo tăng từ khoảng `205 x 193` lên `309 x 229` cell ở 0,05 m/cell và quan sát
gần như toàn bộ lobby thay vì chỉ các wedge có tường nằm trong 8 m.

Regression cuối:

```text
Build: 3 packages finished
Tests: 26 tests, 0 errors, 0 failures, 0 skipped
Hotel route: INDOOR ROUTE PASS
```

### Gazebo robot visual startup sequencing — 2026-08-20

CAD và các URI mesh được kiểm tra là hợp lệ; robot cũng render đúng khi chỉ
chạy hotel demo. Hiện tượng robot đôi lúc không xuất hiện xảy ra khi Nav2 và
RViz cùng bắt đầu trong lúc Gazebo vừa spawn và đang dựng khoảng 32 MB mesh.
Không thay CAD và không thêm primitive giả. `nav2_sim.launch.py` hiện khởi động
Gazebo ngay, Nav2 sau 7 giây và RViz sau 9 giây để tách tải khởi động.

Kiểm tra regression:

```bash
./scripts/build_workspace.sh
source install/setup.bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

```text
Build: 3 packages finished
Tests: 27 tests, 0 errors, 0 failures, 0 skipped
```

Runtime được chạy trong domain và Gazebo partition cô lập:

```bash
ROS_DOMAIN_ID=231 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ./scripts/run_nav2_sim.sh \
  transport_partition:=openarm_nav_visual_postfix3
```

Robot CAD xuất hiện rõ trên ô spawn màu xanh trước khi Nav2/RViz nạp xong.
Lifecycle log báo toàn bộ managed Nav2 nodes active; truy vấn độc lập xác nhận
`controller_server`, `planner_server` và `bt_navigator` đều `active [3]`.
`/scan` ổn định khoảng 10 Hz và `/odom` khoảng 50 Hz. Session được giữ nguyên,
không gửi navigation goal, để phép kiểm tra này chỉ đo startup/visual và ROS
health, tách khỏi acceptance chuyển động đã ghi ở các mục trước.

### All-in-one launch regression — 2026-08-24

Đã thêm public entry point `all_in_one.launch.py` cho hotel Gazebo world,
robot/lidar, wall-time watchdog, SLAM hoặc saved-map localization, Nav2 và
RViz. Wrapper `scripts/run_nav2_sim.sh` gọi entry point này và vẫn giữ bước
làm sạch Snap GUI environment. `use_sim_time` và `transport_partition` được
truyền tường minh qua các launch con.

Build và automated tests:

```bash
source /opt/ros/jazzy/setup.bash
./scripts/build_workspace.sh
source install/setup.bash
colcon test --packages-select openarm_skeleton_v1_2_description
colcon test --packages-select openarm_skeleton_v1_2_gazebo
colcon test --packages-select openarm_skeleton_v1_2_navigation
colcon test-result --verbose
```

```text
Build: 3 packages finished
Tests: 28 tests, 0 errors, 0 failures, 0 skipped
all_in_one.launch.py --show-args: PASS
```

Runtime command attempted by the managed coding environment:

```bash
ROS_LOG_DIR=/tmp/openarm_all_in_one_logs \
ROS_DOMAIN_ID=230 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ./scripts/run_nav2_sim.sh \
  headless:=true use_rviz:=false \
  transport_partition:=openarm_all_in_one_acceptance
```

The launch resolved the new all-in-one entry point and began Gazebo, bridge
and watchdog startup. Runtime acceptance could not continue because this
managed sandbox denied DDS/Gazebo socket access (`getifaddrs: Operation not
permitted`) and made `~/.gz` read-only. This is recorded as **environment
blocked**, not runtime PASS and not a robot-source failure. The same command
must be rerun from the normal desktop terminal; successful Nav2 runtime
acceptance criteria remain `/scan`, full TF chain, active lifecycle/costmaps
and a completed `check_nav2_goal.py` goal as documented above.
