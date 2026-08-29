# Isaac Sim 5.0 + ROS 2 Jazzy — OpenArm Skeleton v1.2

## Trạng thái máy đã kiểm tra ngày 2026-08-29

- Ubuntu 24.04.4 LTS và ROS 2 Jazzy: đúng nền tảng được NVIDIA hỗ trợ.
- GPU NVIDIA GeForce RTX 4060 Laptop, kernel driver 595.84 đã được nạp.
- Khoảng 16 GB RAM, 4 GB swap và hơn 230 GB dung lượng trống.
- Isaac Sim chưa tồn tại ở `~/isaacsim`, `~/Downloads`, `~/.local` hoặc `/opt`.

NVIDIA ghi mức RAM tối thiểu của Isaac Sim 5.0 là 32 GB và GPU tối thiểu là
RTX 4080. Máy này thấp hơn mức chính thức dù trước đây đã từng chạy được 5.0.
Vì vậy integration này dùng room primitive nhỏ, không texture/camera và chỉ
một RTX lidar. Không mở đồng thời Gazebo hoặc ứng dụng GPU nặng.

Nguồn chính thức:

- [Download Isaac Sim 5.0](https://docs.isaacsim.omniverse.nvidia.com/5.0.0/installation/download.html)
- [Cài workstation](https://docs.isaacsim.omniverse.nvidia.com/5.0.0/installation/install_workstation.html)
- [ROS 2 Jazzy trên Ubuntu 24.04](https://docs.isaacsim.omniverse.nvidia.com/5.0.0/installation/install_ros.html)
- [Yêu cầu phần cứng](https://docs.isaacsim.omniverse.nvidia.com/5.0.0/installation/requirements.html)

## 1. Cài Isaac Sim 5.0 standalone

Tải file Linux `isaac-sim-standalone-5.0.0-linux-x86_64.zip` từ trang NVIDIA
ở trên. Sau khi file đã nằm trong `~/Downloads`, chạy:

```bash
mkdir -p "$HOME/isaacsim"
unzip "$HOME/Downloads/isaac-sim-standalone-5.0.0-linux-x86_64.zip" \
  -d "$HOME/isaacsim"
cd "$HOME/isaacsim"
./post_install.sh
./isaac-sim.selector.sh
```

Lần đầu shader cache có thể mất nhiều phút. Trong App Selector chọn
**Isaac Sim Full** để xác nhận GUI cơ bản mở được, rồi đóng nó trước khi chạy
project. Nếu file zip có tên khác, thay đúng tên file đã tải.

Không cần cài ROS riêng bên trong Isaac. Tiến trình simulator dùng thư viện
Jazzy/Python 3.11 đóng gói trong Isaac; các node workspace dùng Jazzy hệ thống
với Python 3.12 và trao đổi qua DDS. Launch của project tự tách hai môi trường
để tránh trộn binary Python.

## 2. Build và kiểm tra host

Từ workspace:

```bash
./scripts/build_workspace.sh
export ISAAC_SIM_PATH="$HOME/isaacsim"
./scripts/check_isaac_host.sh
```

`check_isaac_host.sh` phải tìm thấy `python.sh`. Chạy `nvidia-smi` trong
terminal desktop bình thường; nếu lệnh này lỗi ở đó thì sửa driver trước.

## 3. Một launch chạy toàn bộ

Lệnh khuyến nghị:

```bash
export ISAAC_SIM_PATH="$HOME/isaacsim"
./scripts/run_isaac_nav2.sh
```

Wrapper trên gọi đúng một ROS launch:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch openarm_skeleton_v1_2_isaac isaac_nav2.launch.py \
  isaac_sim_path:="$HOME/isaacsim"
```

Launch thực hiện theo thứ tự:

1. chuẩn bị URDF Isaac từ base-demo đã kiểm chứng;
2. mở scene nhẹ, robot và RTX lidar trong Isaac Sim;
3. mở `robot_state_publisher` và watchdog;
4. đợi `/clock`, `/scan`, `/odom`, `/joint_states` và TF đầy đủ;
5. chỉ khi checker PASS mới khởi động SLAM Toolbox, Nav2 và RViz.

Trong terminal cần thấy `OPENARM ISAAC READY`, sau đó
`PASS: Isaac topics and TF contract are ready for SLAM/Nav2`. Khi RViz mở,
di chuyển robot để tạo map rồi gửi `Nav2 Goal` như với Gazebo.

Headless:

```bash
./scripts/run_isaac_nav2.sh headless:=true use_rviz:=false
```

Localization bằng map đã lưu:

```bash
./scripts/run_isaac_nav2.sh \
  slam:=false map:="$(pwd)/maps/hotel.yaml"
```

## 4. Hợp đồng ROS

```text
Nav2 -> /cmd_vel_nav -> velocity_smoother -> /cmd_vel
     -> wall-time watchdog (0.5 s) -> /cmd_vel_safe -> Isaac controller

Isaac -> /clock
Isaac -> /scan             frame base_scan
Isaac -> /odom             frame odom
Isaac -> /joint_states
Isaac -> odom -> base_footprint
robot_state_publisher -> base_footprint -> base_link -> base_scan -> robot
```

Isaac không subscribe trực tiếp `/cmd_vel`. Nếu Nav2 hoặc teleop chết, watchdog
vẫn phát zero sau 0,5 giây. Hai drive joint dùng bán kính bánh `0.03810 m`,
khoảng cách bánh `0.45 m`; bốn caster joint được giữ passive.

## 5. Kiểm tra độc lập

Khi simulator đang chạy:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run openarm_skeleton_v1_2_isaac check_isaac_runtime.py --timeout 45
```

Kiểm tra command ngắn, watchdog sẽ tự dừng sau khi publisher kết thúc:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.10}, angular: {z: 0.0}}"
```

Nhấn `Ctrl+C` sau khoảng 2 giây và xác nhận robot dừng. Sau đó chạy acceptance
goal Nav2 trong vùng trống:

```bash
ros2 run openarm_skeleton_v1_2_navigation check_nav2_goal.py
```

## 6. Nếu không chạy được

- `Isaac Sim python.sh not found`: đặt đúng `ISAAC_SIM_PATH` tới thư mục có
  `python.sh`, không trỏ tới file zip.
- GUI đóng khi compile shader hoặc máy swap mạnh: đóng Gazebo/browser, thử
  `headless:=true use_rviz:=false`; giới hạn RAM 16 GB vẫn có thể làm runtime
  không ổn định.
- Không có topic ROS: bảo đảm mọi terminal dùng cùng `ROS_DOMAIN_ID`; không
  source workspace ROS bên trong một terminal dùng để chạy `python.sh` thủ công.
- Cache/version conflict: dùng `./isaac-sim.sh --reset-user` hoặc
  `./clear_caches.sh` theo hướng dẫn NVIDIA, rồi thử lại.
- Không đổi launch sang Isaac Sim 6.0 mà không migration: ROS OmniGraph và
  sensor API 6.0 có thay đổi; profile hiện được khóa cho 5.0.
