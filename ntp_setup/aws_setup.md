# IP Design (AWS, AZ - eu-north-1c)

- NTP Client (`ens5`) → `172.31.0.10/20`
- NTP Defense
  - `ens5` (client-facing) → 172.31.0.20/20
  - `ens6` (server-facing) → 172.31.0.30/20
- NTP Server (`ens5`) → 172.31.0.40/20

# Network Routing & ARP Configuration

## 1. Client (`172.31.0.10/20`)
```bash
sudo ip route add 172.31.0.40 via 172.31.0.20 dev ens5
sudo arp -s 172.31.0.20 0e:98:87:aa:82:07  # Defense ens5 MAC address
```

## 2. Server (`172.31.0.40/20`)
```bash
sudo ip route add 172.31.0.10 via 172.31.0.30 dev ens5
sudo arp -s 172.31.0.30 0e:fc:f9:7f:2e:77  # Defense ens6 MAC address
```

## 3. Defense (Middlebox)
```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

# Notes

- Ensure all instances are in the same AZ: `eu-north-1c`.
- Verify MAC addresses using `ip link show dev <interface>`.
- Use `tcpdump` on Defense to validate packet flow (e.g., `udp port 123` for NTP).
