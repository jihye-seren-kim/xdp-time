import csv
import time
from ntplib import NTPClient
import argparse

def rate_limiting_test(server, qps, duration):
    client = NTPClient()
    interval = 1 / qps
    results = []
    successful_requests = 0
    failed_requests = 0
    start_time = time.time()
    last_recorded_time = start_time
    
    while time.time() - start_time < duration:
        try:
            client.request(server)
            successful_requests += 1
        except Exception as e:
            failed_requests += 1

        time.sleep(interval)
        
        # Check if a second has passed
        current_time = time.time()
        if current_time - last_recorded_time >= 1:
            results.append({
                "Server": server,
                "Time Elapsed(s)": int(current_time - start_time),
                "Successful Requests": successful_requests,
                "Failed Requests": failed_requests
            })
            successful_requests = 0
            failed_requests = 0
            last_recorded_time = current_time
    
    return results

def process_all_servers(input_csv, output_csv, qps, duration):
    all_results = []

    with open(input_csv, newline='') as f:
        reader = csv.DictReader(f)
        servers = [row['server'] for row in reader]

    for server in servers:
        print(f"\nTesting {server}...")
        try:
            results = rate_limiting_test(server, qps, duration)
            all_results.extend(results)
        except Exception as e:
            print(f"Error testing server {server}: {e}")

    with open(output_csv, 'w', newline='') as f:
        fieldnames = ["Server", "Time Elapsed(s)", "Successful Requests", "Failed Requests"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nAll results saved to {output_csv}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NTP server rate limiting test")
    parser.add_argument("--input", type=str, default="ntp_list.csv", help="CSV file with list of NTP servers")
    parser.add_argument("--output", type=str, default="rate_limiting_results.csv", help="Output CSV file for results")
    parser.add_argument("--qps", type=int, required=True, help="Queries per second")
    parser.add_argument("--duration", type=int, required=True, help="Test duration in seconds")

    args = parser.parse_args()
    process_all_servers(args.input, args.output, args.qps, args.duration)
