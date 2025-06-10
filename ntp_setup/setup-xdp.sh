#!/bin/bash
set -e

echo "[+] Installing dependencies..."
sudo apt update
sudo apt install -y clang llvm ethtool iproute2 bpfcc-tools libelf-dev gcc-multilib build-essential
sudo apt install linux-headers-$(uname -r) linux-image-$(uname -r)
sudo apt install dwarves
sudo bpftool btf dump file /sys/kernel/btf/vmlinux format c | head

echo "[+] Compiling XDP programs..."
clang -O2 -g -target bpf -D__TARGET_ARCH_x86 -c cs_ratelimit.c -o cs_ratelimit.o
clang -O2 -g -target bpf -D__TARGET_ARCH_x86 -c sc_amppre.c -o sc_amppre.o

echo "[+] Setting MTU and NIC queues..."
sudo ip link set ens6 mtu 1500
sudo ip link set ens7 mtu 1500
sudo ethtool -L ens6 combined 1
sudo ethtool -L ens7 combined 1

echo "[+] Attaching XDP programs..."
sudo ip link set dev ens6 xdp obj cs_ratelimit.o sec xdp
sudo ip link set dev ens7 xdp obj sc_amppre.o sec xdp

# /sys/fs/bpf/xdp/globals : check the pinning map 
