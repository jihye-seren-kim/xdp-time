// common.h
#ifndef __COMMON_HELPERS_H__
#define __COMMON_HELPERS_H__

struct {
    __uint(type, BPF_MAP_TYPE_DEVMAP);
    __uint(max_entries, 16);
    __type(key, __u32);
    __type(value, __u32);
} redirect_map SEC(".maps");

#endif
