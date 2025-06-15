#ifndef __NTP_H__
#define __NTP_H__

#include <linux/types.h>

#define NTP_PORT 123
#define NTP_HEADER_LEN 48

// NTP Header structure (RFC 5905)
struct ntp_header {
    __u8 li_vn_mode;       // Leap Indicator (2), Version Number (3), Mode (3)
    __u8 stratum;          // Stratum level
    __u8 poll;             // Poll interval
    __u8 precision;        // Precision

    __u32 root_delay;      // Total round trip delay
    __u32 root_dispersion; // Max error
    __u32 ref_id;          // Reference ID

    __u64 ref_timestamp;   // Reference timestamp
    __u64 orig_timestamp;  // Originate timestamp
    __u64 recv_timestamp;  // Receive timestamp
    __u64 tx_timestamp;    // Transmit timestamp
};

// NTP Extension Field Header (RFC 7822)
struct ntp_ext_field {
    __u16 field_type;      // Extension Field Type (e.g., 0x0104 = NTS)
    __u16 field_length;    // Total length in bytes (including type/length)
    __u8  value[];         // Extension data (variable)
} __attribute__((packed));

/*
 Example use cases for NTP Extension Fields:
 - NTS-KE (Key Exchange) records
 - Authenticator and cookie extensions
 - NTP Control Extensions (future use)
*/

#endif /* __NTP_H__ */
