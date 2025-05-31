#!/bin/bash
set -e

echo "[+] Installing dependencies..."
sudo apt update
sudo apt install -y clang llvm ethtool iproute2 bpfcc-tools libelf-dev gcc-multilib build-essential

echo "[+] Compiling XDP programs..."
clang -O2 -target bpf -c cs_ratelimit.c -o cs_ratelimit.o -g -D__TARGET_ARCH_x86
clang -O2 -target bpf -c sc_amppre.c -o sc_amppre.o -g -D__TARGET_ARCH_x86

echo "[+] Setting MTU and NIC queues..."
sudo ip link set ens6 mtu 1500
sudo ip link set ens7 mtu 1500
sudo ethtool -L ens6 combined 1
sudo ethtool -L ens7 combined 1

echo "[+] Attaching XDP programs..."
sudo ip link set dev ens6 xdp obj cs_ratelimit.o sec xdp
sudo ip link set dev ens7 xdp obj sc_amppre.o sec xdp

echo "[✔] Setup completed."
