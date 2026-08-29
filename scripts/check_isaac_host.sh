#!/usr/bin/env bash
set -o pipefail

echo "OpenArm Isaac Sim host check"
echo "OS: $(. /etc/os-release && echo "$PRETTY_NAME")"
echo "Kernel: $(uname -r)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2 " total, " $7 " available"}')"
echo "Swap: $(free -h | awk '/^Swap:/ {print $2 " total, " $3 " used"}')"
echo "NVIDIA module: $(cat /proc/driver/nvidia/version 2>/dev/null | head -1 || echo unavailable)"

if command -v nvidia-smi >/dev/null 2>&1; then
  if ! nvidia-smi --query-gpu=name,driver_version,memory.total \
      --format=csv,noheader; then
    echo "WARN: nvidia-smi cannot access the GPU from this environment." >&2
  fi
else
  echo "WARN: nvidia-smi is not installed." >&2
fi

isaac_sim_path="${ISAAC_SIM_PATH:-}"
if [[ -n "$isaac_sim_path" && -f "$isaac_sim_path/python.sh" ]]; then
  echo "Isaac Sim: $isaac_sim_path"
  exit 0
fi

echo "Isaac Sim: not found; set ISAAC_SIM_PATH after extracting 5.0." >&2
exit 2
