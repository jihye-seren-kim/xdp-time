# IP Design (AWS, AZ - eu-north-1c)

- NTP Client (`ens5`) → `172.31.0.10/20`, `0e:3e:5c:a3:0b:af`
- NTP Defense
  - `ens5` → SSH/Public IP (`172.31.0.20/20`)
  - `ens6` (client-facing) → `172.31.0.21/20`, `0e:ea:b6:d8:7a:33`  
  - `ens7` (server-facing) → `172.31.0.30/20`, `0e:fc:f9:7f:2e:77`
- NTP Server (`ens5`) → `172.31.0.40/20`, `0e:2b:6c:5c:5b:8d` 

# Network Routing & ARP Configuration

## 1. Client (`172.31.0.10/20`)
```bash
sudo ip route add 172.31.0.40 via 172.31.0.21 dev ens5
sudo ip route add 172.31.0.30 via 172.31.0.21 dev ens5
sudo arp -s 172.31.0.21 0e:ea:b6:d8:7a:33 
```

## 2. Server (`172.31.0.40/20`)
```bash
sudo ip route add 172.31.0.10 via 172.31.0.30 dev ens5
sudo ip route add 172.31.0.20 via 172.31.0.30 dev ens5
sudo arp -s 172.31.0.30 0e:fc:f9:7f:2e:77 
```

## 3. Defense (Middlebox)
```bash
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

```bash
sudo ip route add 172.31.0.10 dev ens6
sudo arp -s 172.31.0.10 0e:3e:5c:a3:0b:af 
sudo ip route add 172.31.0.40 dev ens7
sudo arp -s 172.31.0.40 0e:2b:6c:5c:5b:8d
```

# Notes

- Ensure all instances are in the same AZ: `eu-north-1c`.
- Verify MAC addresses using `ip link show dev <interface>`.
- Use `tcpdump` on Defense to validate packet flow (e.g., `udp port 123` for NTP).
- Ensure to disable Source/Destination Check on the Defense VM in the AWS console
  `Actions > Networking > Change source/dest check > Stop`

# Chrony + NTP Setup (Client & Server)

## 1. Chrony Installation

```bash
sudo apt update
sudo apt install chrony -y
```

## 2. NTP Server (NTS) - TLS certificate Generation

- /etc/chrony/certs/openssl-san.conf

```bash
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
C = DE
ST = Bayern
L = Munich
O = Unibw
CN = ntp-server.local

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = ntp-server.local
```

- Create certificate:
  
```bash
sudo mkdir -p /etc/chrony/certs
cd /etc/chrony/certs

sudo openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout server.key -out server.crt -days 3650 \
  -config openssl-san.conf
```

```bash
sudo chmod 644 server.key
sudo chmod 644 server.crt
```

## 3. NTP Server Configuration (/etc/chrony/chrony.conf)

```bash
server 127.127.1.0

ntsservercert /etc/chrony/certs/nts.crt
ntsserverkey /etc/chrony/certs/nts.key

bindaddress 0.0.0.0
allow 172.31.0.0/16
```

```bash
sudo systemctl restart chronyd
sudo systemctl status chronyd
```

## 4. NTP Client Configuration (/etc/chrony/chrony.conf)

```bash
server ntp-server.local iburst nts
```

```bash
sudo systemctl restart chronyd
sudo systemctl status chronyd
chronyc sources -v
```

## 5. NTS Certificate Installation on Client
   
- Copy ```server.crt``` from server:

```bash
sudo mkdir -p /usr/local/share/ca-certificates/
sudo vim server.crt (copy from server)
sudo update-ca-certificates --fresh
```

- Verify symlink:

```bash
ls -l /etc/ssl/certs | grep server
```
  
- Client Hostname Resolution (/etc/host)

```bash
echo "172.31.0.40 ntp-server.local" | sudo tee -a /etc/hosts
```

- Check `chronyc sources -v`
e.g.,
```bash
MS Name/IP address         Stratum Poll Reach LastRx Last sample               
===============================================================================
^* ntp-server.local              4   6    17     9  -1219ns[-6804ns] +/-  470us
```
