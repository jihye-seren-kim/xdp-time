#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <linux/tcp.h>
#include <linux/icmp.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>
#include "common.h" 

struct rate_info {
    __u64 last_ts; // last timestamp (ms)
    __u32 pkt_count; // number of packet (1-second window)
};

struct mac_addr {
    __u8 addr[6];
    __u8 pad[2];
};

// bpf map (ip-rate)
struct {
    __uint(type, BPF_MAP_TYPE_LRU_PERCPU_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);
    __type(value, struct rate_info);
} ip_rate_map SEC(".maps");

// for mac address
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 16);
    __type(key, __u32);             // ifindex
    __type(value, struct mac_addr); // MAC
} mac_map SEC(".maps");

// ctx -> includes packet metadata
SEC("xdp")
int xdp_ingress_rate_limit(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_DROP;

    if (bpf_ntohs(eth->h_proto) != ETH_P_IP)
        return XDP_DROP;

    struct iphdr *ip = data + sizeof(struct ethhdr);
    if ((void *)(ip + 1) > data_end)
        return XDP_DROP;

    __u32 src_ip = ip->saddr;
    __u64 now = bpf_ktime_get_ns() / 1000000;
    __u32 in_ifindex = ctx->ingress_ifindex;

    // SSH (TCP 22) -> allow
    if (ip->protocol == IPPROTO_TCP) {
        struct tcphdr *tcp = (struct tcphdr *)((void *)ip + ip->ihl * 4);
        if ((void *)(tcp + 1) > data_end)
            return XDP_DROP;
    
        if (tcp->dest == bpf_htons(22) || tcp->source == bpf_htons(22)) 
            return XDP_PASS;
        return XDP_DROP; 
        }

    // ICMP (ping) -> allow
    if (ip->protocol == IPPROTO_ICMP) {
        struct mac_addr *dst_mac = bpf_map_lookup_elem(&mac_map, &in_ifindex);
        if (dst_mac)
            __builtin_memcpy(eth->h_dest, dst_mac->addr, 6);
        return XDP_PASS;
    }

    // Handle only UDP 123 (NTP)
    if (ip->protocol == IPPROTO_UDP) {
        struct udphdr *udp = (struct udphdr *)((void *)ip + ip->ihl * 4);
        if ((void *)udp + sizeof(*udp) > data_end)
            return XDP_DROP;
    
        if (udp->dest == bpf_htons(123) || udp->source == bpf_htons(123)) {
            bpf_printk("NTP packet: src=%x\n", ip->saddr);
            __u64 start = bpf_ktime_get_ns();
      
        // rate limiting logic
            struct rate_info *rinfo = bpf_map_lookup_elem(&ip_rate_map, &src_ip);

            if (rinfo) {
                if (now - rinfo->last_ts < 1000) {
                    rinfo->pkt_count++;
                    if (rinfo->pkt_count > 50) {
                        __u64 end = bpf_ktime_get_ns();
                        __u64 duration = end - start;
                        bpf_printk("DROP triggered for %x at %llu ns\n", src_ip, duration);
                        return XDP_DROP;
                    }
                } else {
                    rinfo->last_ts = now;
                    rinfo->pkt_count = 1;
                }
            } else {
                    struct rate_info new_info = { 
                        .last_ts = now,
                        .pkt_count = 1 
                    };
                    bpf_map_update_elem(&ip_rate_map, &src_ip, &new_info, BPF_ANY);
                }

            __u32 out_ifindex = (in_ifindex == 3) ? 4 : 3; // 예시: 3 ↔ 4
            struct mac_addr *dst_mac = bpf_map_lookup_elem(&mac_map, &out_ifindex);
            if (dst_mac)
                __builtin_memcpy(eth->h_dest, dst_mac->addr, 6);

            __u64 end = bpf_ktime_get_ns();
            bpf_printk("REDIRECT for %x, took %llu ns\n", src_ip, end - start);
            return bpf_redirect_map(&redirect_map, out_ifindex, 0);
        }
    }

    return XDP_DROP; 
}

char _license[] SEC("license") = "GPL";
