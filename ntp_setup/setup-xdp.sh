#!/bin/bash
set -e

# Install required packages
sudo apt update
sudo apt install -y \
  clang llvm libelf-dev gcc-multilib build-essential \
  iproute2 iputils-ping bpfcc-tools \
  linux-tools-$(uname -r) linux-headers-$(uname -r) linux-source ethtool

# Set include path for clang
export C_INCLUDE_PATH=/usr/include/x86_64-linux-gnu

# Compile eBPF programs
clang -O2 -target bpf -c cs_ratelimit.c -o cs_ratelimit.o -g -D__TARGET_ARCH_x86
clang -O2 -target bpf -c sc_amppre.c -o sc_amppre.o -g -D__TARGET_ARCH_x86

# Set MTU to safe value
sudo ip link set ens6 mtu 1500
sudo ip link set ens7 mtu 1500

# Reduce ENA NIC queues to avoid XDP attach failure
sudo ethtool -L ens6 combined 1
sudo ethtool -L ens7 combined 1

# Wait briefly to ensure queue change is applied
sleep 2

# Attach XDP programs to interfaces
sudo ip link set dev ens6 xdp obj cs_ratelimit.o sec xdp
sudo ip link set dev ens7 xdp obj sc_amppre.o sec xdp

# Print success message
echo "[+] XDP programs successfully attached to ens6 and ens7"
