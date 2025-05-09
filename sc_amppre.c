#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>
#include "common.h"

struct amp_info {
        __u64 req_size;
        __u64 resp_size;
};

// amplification map (dst_ip : request/response size)
struct {
        __uint(type, BPF_MAP_TYPE_LRU_PERCPU_HASH);
        __uint(max_entries, 1024);
        __type(key, __u32);
        __type(value, struct amp_info);
} amp_map SEC(".maps");

SEC("xdp")
int xdp_egress_amplification(struct xdp_md *ctx) {
        void *data_end = (void *)(long)ctx->data_end;
        void *data = (void *)(long)ctx->data;

        struct ethhdr *eth = data;
        if ((void *)(eth + 1) > data_end)
                return XDP_DROP;

        if (eth->h_proto != __constant_htons(ETH_P_IP))
                return XDP_DROP;

        struct iphdr *ip = data + sizeof(struct ethhdr);
        if ((void *)(ip + 1) > data_end)
                return XDP_DROP;

        if (ip->protocol != IPPROTO_UDP)
                return XDP_DROP;

        int ip_header_len = ip->ihl * 4;
        int udp_payload_len = bpf_ntohs(ip->tot_len) - ip_header_len;

        __u32 dst_ip = bpf_ntohl(ip->daddr);

        struct amp_info *ainfo;
        ainfo = bpf_map_lookup_elem(&amp_map, &dst_ip);

        if(ainfo) {
                ainfo->resp_size += udp_payload_len;
                if (ainfo->resp_size > (ainfo->req_size * 5)) {
                        return XDP_DROP;
                }
        } else {
                struct amp_info new_info = { .req_size = udp_payload_len, .resp_size = udp_payload_len };
                bpf_map_update_elem(&amp_map, &dst_ip, &new_info, BPF_ANY);
        }

        __u32 ifindex = 3; 
        return bpf_redirect_map(&redirect_map, ifindex, 0);
}

char _license[] SEC("license") = "GPL";