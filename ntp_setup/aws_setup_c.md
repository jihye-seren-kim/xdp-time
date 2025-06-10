# IP Design (AWS, AZ - eu-north-1c)

- NTP Client (`ens5`) → `172.31.0.10/20`, `0e:3e:5c:a3:0b:af`
- NTP Defense + Server
  - `ens5` (SSH only): `172.31.0.20/20`
  - `ens6` (ingress: client → server): `172.31.0.30/20`, `0e:fc:f9:7f:2e:77`  
  - `ens7` (egress: server → client): `172.31.0.40/20`, `0e:1b:c6:ec:18:7f`

# Network Routing & ARP Configuration

## 1. Client (`172.31.0.10/20`)
```bash
sudo arp -s 172.31.0.30 0e:fc:f9:7f:2e:77
```

## 2. Server + Defense (`172.31.0.30/20, 172.31.0.40/20`)
```bash
ip route add 172.31.0.10 dev ens7
```

```bash
echo 0 | sudo tee /proc/sys/net/ipv4/conf/all/rp_filter
```

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

ntsservercert /etc/chrony/certs/server.crt
ntsserverkey /etc/chrony/certs/server.key

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
echo "172.31.0.30 ntp-server.local" | sudo tee -a /etc/hosts
```

```bash
sudo systemctl restart chronyd
sudo systemctl status chronyd
chronyc sources -v
```

- Check `chronyc sources -v`
e.g.,
```bash
MS Name/IP address         Stratum Poll Reach LastRx Last sample               
===============================================================================
^* ntp-server.local              4   6    17     9  -1219ns[-6804ns] +/-  470us
^* ntp-server.local              4   6    17     2  +9077ns[  +23us] +/-  471us
^* ntp-server.local              4   6    37    44    -54ns[  +25us] +/-  286us
^* ntp-server.local              4   6    77     7    +43us[  +63us] +/-  347us
```
