import csv
from ntplib import NTPClient
from time import ctime

def query_ntp(server):
    client = NTPClient()
    try:
        response = client.request(server)
        return {
            "Server": server,
            "Offset": response.offset,
            "Delay": response.delay,
            "Version": response.version,
            "Stratum": response.stratum,
            "Precision": response.precision,
            "Poll Interval": 2**response.poll,
            "Mode": response.mode,
            "Server Time": ctime(response.tx_time),
            "Root Delay": response.root_delay,
            "Root Dispersion": response.root_dispersion,
            "Leap Indicator": response.leap,
            "Reference Time": ctime(response.ref_time) if response.ref_time else None,
            "Receive Time": ctime(response.recv_time) if response.recv_time else None,
            "Originate Time": ctime(response.orig_time) if response.orig_time else None,
            "Error": "None"
        }
    except Exception as e:
        return {
            "Server": server,
            "Offset": None,
            "Delay": None,
            "Version": None,
            "Stratum": None,
            "Precision": None,
            "Poll Interval": None,
            "Mode": None,
            "Server Time": None,
            "Root Delay": None,
            "Root Dispersion": None,
            "Leap Indicator": None,
            "Reference Time": None,
            "Receive Time": None,
            "Originate Time": None,
            "Error": str(e)
        }

def process_ntp_servers(input_csv, output_csv):

    results = []

    with open(input_csv, mode='r') as infile:
        reader = csv.reader(infile)
        servers = [row[0] for row in reader] 

    for server in servers:
        print(f"Querying NTP Server: {server}")
        result = query_ntp(server)
        results.append(result)

    with open(output_csv, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=[
            "Server", "Offset", "Delay", "Version", "Stratum", 
            "Precision", "Poll Interval", "Mode", "Server Time", 
            "Root Delay", "Root Dispersion", "Leap Indicator",
            "Reference Time", "Receive Time", "Originate Time", "Error"
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {output_csv}")

input_csv = "ntp_list.csv" 
output_csv = "ntp_results.csv"  
process_ntp_servers(input_csv, output_csv)

# sudo nmap -Pn -sU -p123 --script ntp-info -n time.apple.com
