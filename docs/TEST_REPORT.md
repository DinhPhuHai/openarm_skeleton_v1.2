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

### One-file bootstrap launcher regression — 2026-08-24

Đã thêm `START_OPENARM.sh` làm file bootstrap độc lập. Khi nằm ngoài
repository, file clone nhánh `main` chính thức vào
`~/openarm_skeleton_v1.2_ws`; khi nằm trong workspace, file dùng chính
workspace đó. Update chỉ dùng `fetch` và `merge --ff-only`, đồng thời tự bỏ
qua bước update nếu working tree có thay đổi để không ghi đè source local.

Chuỗi launcher đã được khóa bằng contract test: kiểm tra executable bit, chạy
`bash -n`, và xác nhận đủ các bước clone, dependency installer, `rosdep`, build
cùng `run_nav2_sim.sh`. Lệnh regression:

```bash
bash -n START_OPENARM.sh
./START_OPENARM.sh --help
source /opt/ros/jazzy/setup.bash
./scripts/build_workspace.sh
source install/setup.bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

```text
Build: 3 packages finished
Tests: 29 tests, 0 errors, 0 failures, 0 skipped
START_OPENARM.sh syntax/help/contract: PASS
```

Không chạy full GUI runtime từ coding sandbox trong mục này vì giới hạn socket
đã ghi ở mục all-in-one ngay phía trên. Launcher cuối cùng gọi đúng
`run_nav2_sim.sh`; runtime desktop của launch stack bên dưới vẫn dùng acceptance
SLAM/Nav2 đã ghi trong báo cáo này.

### Isaac Sim 5.0 integration — 2026-08-29

Host được kiểm tra trước khi tích hợp:

```text
OS: Ubuntu 24.04.4 LTS
GPU: NVIDIA GeForce RTX 4060 Max-Q / Mobile
NVIDIA kernel module: 595.84
RAM: khoảng 16 GB; swap: 4 GB
Disk trống: hơn 230 GB
Isaac Sim standalone/Python package: không tìm thấy
```

Ubuntu 24.04 và Jazzy đúng ma trận hỗ trợ Isaac Sim 5.0. Tuy nhiên 16 GB RAM
thấp hơn mức tối thiểu 32 GB NVIDIA công bố; vì thế source chỉ tạo room
primitive nhẹ, một robot và một RTX lidar. Không dùng warehouse/texture/camera.

Đã thêm package `openarm_skeleton_v1_2_isaac` với các contract sau:

- chuẩn bị URDF riêng: bỏ mọi tag Gazebo, resolve đủ 34 STL thành path tuyệt
  đối và thêm inertia cực nhỏ cho ba frame-only link;
- chỉ sáu joint mobile-base được phép movable; bốn caster được release passive;
- differential controller dùng `drive_joint_1`, `drive_joint_2`, wheel radius
  `0.03810 m` và wheel distance `0.45 m`;
- Isaac chỉ subscribe `/cmd_vel_safe`, phía trước vẫn là watchdog wall-time
  0,5 giây;
- RTX lidar dùng profile 2D `Example_Rotary_2D`; xuất `/clock`, `/scan`,
  `/odom`, `/joint_states` và
  `odom -> base_footprint`; `robot_state_publisher` hoàn thiện phần TF robot;
- readiness checker phải thấy đủ topic cùng TF
  `odom -> base_footprint -> base_link -> base_scan` trước khi mở SLAM/Nav2;
- tiến trình Isaac loại ROS Jazzy Python 3.12 khỏi environment để dùng ROS
  Jazzy/Python 3.11 nội bộ của Isaac, giao tiếp với node ngoài bằng Fast DDS.

Build và full regression:

```bash
source /opt/ros/jazzy/setup.bash
./scripts/build_workspace.sh
source install/setup.bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

```text
Build: 4 packages finished
Tests: 36 tests, 0 errors, 0 failures, 0 skipped
Isaac contract tests: 6 passed
```

ROS launch được smoke-test không có simulator với timeout 1 giây. RSP và
watchdog khởi động đúng; checker báo chính xác thiếu bốn topic Isaac rồi launch
dừng sạch, không xảy ra lỗi shutdown adapter. Thử path bundle không hợp lệ trả
ngay lỗi có hướng dẫn:

```text
Isaac Sim python.sh not found. Set
isaac_sim_path:=/absolute/path/to/isaac-sim-5.0.0
```

Full Isaac GUI/headless runtime chưa được chạy vì bundle chưa được cài trên
máy và coding sandbox không truy cập được GPU/DDS socket (`nvidia-smi` không
communicate được với driver; DDS báo `Operation not permitted`). Trạng thái là
**environment blocked**, không phải runtime PASS. Sau khi người dùng tải
standalone 5.0, acceptance còn lại phải chạy trong desktop terminal:

```bash
export ISAAC_SIM_PATH="$HOME/isaacsim"
./scripts/check_isaac_host.sh
./scripts/run_isaac_nav2.sh
```

PASS cuối yêu cầu log `OPENARM ISAAC READY`, readiness checker PASS, robot
render đúng, command thẳng/quay đúng dấu, watchdog dừng robot, SLAM map ổn
định và `check_nav2_goal.py` thành công.

### Isaac Sim 5.0 first native runtime — 2026-08-31

Bundle standalone đã được tải, kiểm tra CRC và cài tại `/home/hai/isaacsim`.
GPU runtime nhìn thấy RTX 4060 Laptop 8 GB, NVIDIA driver 595.84 và Vulkan.

Lần chạy project đầu tiên phát hiện validator URDF từ chối nhầm mesh symlink
của `colcon --symlink-install`. Validator đã được sửa để vẫn chặn URI tuyệt đối
và `..`, nhưng chấp nhận package asset symlink hợp lệ; regression test mới tái
tạo đúng install layout. Kết quả sau sửa:

```text
Isaac package contract: 7 passed
Workspace aggregate: 37 tests, 0 errors, 0 failures, 0 skipped
```

Sau đó project đi qua bước mesh nhưng Isaac Kit segfault khi khởi tạo RTX:

```text
Warp CUDA error: Failed to get driver entry point 'cuDeviceGetUuid'
Warp CUDA error 36: API call is not supported in the installed CUDA driver
librtx.scenedb.plugin.so
exit code 139 (SIGSEGV)
```

Để tách project khỏi nguyên nhân, Isaac nguyên bản cũng được chạy không ROS,
factory reset, headless, single GPU và tắt driver-version verification:

```bash
cd /home/hai/isaacsim
./isaac-sim.sh --no-window --reset-user \
  --/renderer/multiGpu/enabled=false \
  --/renderer/activeGpu=0 \
  --/rtx/verifyDriverVersion/enabled=false
```

Kết quả vẫn cùng backtrace RTX và exit 139. Do đó blocker là NVIDIA 595.84
không tương thích với Isaac Sim 5.x/Kit 107, không phải OpenArm, ROS, Nav2,
IOMMU hay lựa chọn GUI/headless. NVIDIA support xác nhận chữ ký crash này với
nhánh 595.x và khuyến nghị nhánh driver 580 đã validate. Project host checker
giờ chặn driver >=595 trước khi mở Isaac. Full runtime vẫn **blocked** cho tới
khi đổi về driver 580, reboot và chạy lại acceptance.

### Isaac Sim 5.0 driver 580 và Jazzy/Nav2 acceptance — 2026-08-31

Sau khi đổi driver và reboot, kernel module, NVIDIA userspace libraries và GPU
đều được xác nhận dùng cùng phiên bản `580.173.02`. `check_isaac_host.sh` PASS.
Isaac factory headless chạy tới `app ready`, ổn định đủ 60 giây và chỉ dừng do
timeout chủ động (`124`), không còn SIGSEGV/exit 139.

Native runtime đầu tiên sau khi đổi driver phát hiện launch đã loại
`ROS_DISTRO` nhưng chưa thêm đường dẫn ROS Jazzy nội bộ của Isaac. Bridge vì
thế fallback Humble và không tìm thấy `librmw_fastrtps_cpp.so`. Launch đã được
sửa để:

- giữ ROS Jazzy hệ thống/Python 3.12 ngoài tiến trình simulator;
- đặt `ROS_DISTRO=jazzy`, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` cho Isaac;
- prepend `isaacsim.ros2.bridge/jazzy/lib` của bundle vào `LD_LIBRARY_PATH`;
- báo lỗi ngay nếu bundle không có thư viện Jazzy;
- flush marker `OPENARM ISAAC READY`/`ERROR` vào launch log.

Runtime acceptance chạy trong domain Fast DDS hợp lệ, không giới hạn frame:

```bash
export ISAAC_SIM_PATH=/home/hai/isaacsim
export ROS_DOMAIN_ID=143
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
./scripts/run_isaac_nav2.sh \
  headless:=true use_rviz:=false max_frames:=0 startup_timeout:=300

# Terminal thứ hai, cùng ROS_DOMAIN_ID
ros2 run openarm_skeleton_v1_2_navigation check_nav2_goal.py \
  --goal-distance 0.60 --min-motion 0.25 --goal-timeout 80
```

Kết quả:

```text
Driver: 580.173.02; RTX 4060 Laptop 8188 MiB
Isaac ROS bridge: internal rclpy for ROS Distro jazzy loaded
PASS: Isaac topics and TF contract are ready for SLAM/Nav2
SLAM lifecycle: active; lidar registered
Nav2 controller/planner/bt_navigator: active
Local/global costmaps: active and publishing
/scan: about 24 Hz
Nav2: Goal succeeded
PASS: action_status=4, goal_distance=0.600 m,
      odom_motion=0.531 m, along_track=0.531 m,
      cross_track=0.023 m, max_cross_track=0.050 m
```

Đây là headless runtime PASS cho driver, Isaac, robot import, ROS topic/TF,
SLAM, costmaps và Nav2 movement. GUI rendering vẫn nên được người dùng quan
sát trực tiếp khi chạy lệnh mặc định không có `headless:=true`.

Full regression sau bản sửa:

```text
Build: 4 packages finished
Tests: 38 tests, 0 errors, 0 failures, 0 skipped
Isaac contract: 8 passed
```

### Isaac turning/Nav2 side-goal correction — 2026-08-31

Kiểm tra bổ sung sau phản hồi robot chỉ tiến thẳng đã tìm thấy ba nguyên nhân
riêng của runtime Isaac (Gazebo không bị ảnh hưởng):

- `velocity_smoother` ở `CLOSED_LOOP` bị giữ tại bước đầu `0.05 rad/s` vì
  twist do `IsaacComputeOdometry` báo sai trong khi pose vẫn đúng;
- angular drive damping `10` quá nhỏ theo đơn vị drive USD, làm bánh chỉ đạt
  khoảng `0.2 rad/s` và quay tại chỗ rất yếu;
- khi đã gần goal, Regulated Pure Pursuit yêu cầu đúng `0.05 rad/s`, thấp hơn
  ma sát tĩnh của mô hình nên không thể chỉnh nốt góc goal.

Bản sửa giữ cấu hình Gazebo `CLOSED_LOOP`, nhưng launch Isaac override smoother
sang `OPEN_LOOP`; tăng wheel-drive damping lên `1.0e5` với max force vẫn giới
hạn ở `30`; đổi odometry gốc thành `/isaac_odom_raw` rồi suy ra planar twist từ
pose/simulation time; và thêm conditioner sau watchdog để nâng lệnh quay khác
zero lên tối thiểu `0.25 rad/s` (`0.15` vẫn stall trong GUI dù headless PASS).
Zero không bị thay đổi nên timeout safety vẫn
dừng robot. Navigation được trì hoãn 3 giây sau SLAM để tránh lifecycle service
timeout khi CPU đang tải RTX. Kiểm tra GUI sau đó cho thấy RViz mở ở giây thứ
5 vẫn có thể làm timeout `smoother_server/change_state`, nên RViz được dời tới
giây thứ 15; người dùng chỉ gửi goal sau `Managed nodes are active`.

Runtime acceptance cuối chạy Isaac headless, Fast DDS domain 152. Goal buộc
robot đổi hướng 90 độ rồi đi sang bên hông:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: odom}, pose: {position: {x: 0.0, y: 0.60}, orientation: {z: 0.70710678, w: 0.70710678}}}}"
```

Kết quả:

```text
Goal accepted with ID: b1ec38e9bb2841bfa78a9f8c97a09c90
error_code: 0
Goal finished with status: SUCCEEDED
Final odom position: x=0.0081 m, y=0.6154 m
Final orientation: z=0.7049, w=0.7093 (about 89.5 degrees)
Position error: about 0.017 m; heading error: about 0.5 degrees
/cmd_vel_safe after goal: all zero
/isaac_cmd_vel after goal: all zero
```

Full regression sau correction:

```text
Build: 4 packages finished
Tests: 40 tests, 0 errors, 0 failures, 0 skipped
Navigation contract: 8 passed
Isaac contract: 10 passed
```

GUI retest sau phản hồi vận tốc quay vẫn stall:

- xóa các node test mồ côi ở ROS domain 151/152 trước khi mở phiên mới;
- tăng minimum angular conditioner từ `0.15` lên `0.25 rad/s`;
- dời RViz từ giây 5 tới giây 15. Trước thay đổi, RViz tải đồng thời làm
  `smoother_server/change_state` timeout và action server không xuất hiện;
- phiên mới đạt `Managed nodes are active` trước khi RViz mở;
- `/spin` 0.8 rad hoàn thành `SUCCEEDED` trong GUI;
- goal lệch 90 độ `(0.0, 0.60)` hoàn thành `SUCCEEDED`, final odom
  `(0.0027, 0.6158)`.

Log phiên lỗi cũng ghi nhiều `Received goal preemption request`: nhấn goal mới
trước khi goal cũ hoàn thành sẽ chủ động hủy hướng cũ. Khi demo, chỉ gửi một
goal và chờ trạng thái `SUCCEEDED` hoặc `FAILED` trước goal tiếp theo.

### Isaac hotel/restaurant selectable scenes — 2026-09-01

Isaac integration được mở rộng từ một room mẫu thành hai scene primitive nhẹ,
chọn bằng launch argument `scene:=hotel` hoặc `scene:=restaurant`. Hotel có
sảnh lễ tân, khu sofa, vách hành lang, thang máy và xe hành lý; restaurant có
khu bếp/quầy phục vụ, bục đón khách và bốn cụm bàn ghế. Tất cả furniture đều
có collision, nằm trong tầm quét lidar và giữ vùng spawn bán kính 0,90 m trống.

Build và contract test ban đầu:

```text
Build: 4 packages finished
Isaac contract: 12 passed
isaac_nav2.launch.py --show-args: scene default hotel, choices documented
```

Hai runtime được chạy tuần tự, headless, mỗi runtime dùng ROS domain riêng để
không lẫn discovery:

```bash
ROS_DOMAIN_ID=161 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ./scripts/run_isaac_nav2.sh \
  scene:=hotel headless:=true use_rviz:=false startup_timeout:=300

ROS_DOMAIN_ID=162 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
  ./scripts/run_isaac_nav2.sh \
  scene:=restaurant headless:=true use_rviz:=false startup_timeout:=300
```

Trong từng domain đã chạy `check_isaac_runtime.py --timeout 30`, sau đó
`check_nav2_goal.py --goal-distance 0.60 --min-motion 0.25 --goal-timeout 90`.
Kết quả:

```text
Hotel:
  Isaac topics + TF: PASS
  Nav2 lifecycle + costmaps: active
  Goal: SUCCEEDED; odom_motion=0.550 m; cross_track=-0.000 m

Restaurant:
  Isaac topics + TF: PASS
  Nav2 lifecycle + costmaps: active
  Goal: SUCCEEDED; odom_motion=0.542 m; cross_track=0.001 m
```

Acceptance này xác nhận scene được tạo thật trong Isaac, lidar/SLAM nhận vật
cản và Nav2 điều khiển robot thành công ở cả hai bố trí. Occupancy map 2D vẫn
là sản phẩm của SLAM; cần khám phá rồi lưu riêng thành `isaac_hotel.yaml` và
`isaac_restaurant.yaml`, không dùng chéo giữa hai scene.

Full regression cuối và kiểm tra shutdown:

```text
Build: 4 packages finished
Tests: 42 tests, 0 errors, 0 failures, 0 skipped
SIGINT command conditioner: exit 0
SIGINT odometry corrector: exit 0
```

Hai node Python phụ trước đó có thể in traceback `rcl_shutdown already called`
khi launch nhận `Ctrl+C`, dù runtime đã PASS. Cleanup giờ bắt
`KeyboardInterrupt`, chỉ gọi shutdown khi context còn active và thoát sạch.
