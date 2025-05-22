import csv
import subprocess
import socket
import ssl

def check_ntp_authentication(server):
    try:
        # Run ntpq to get the server variables
        result = subprocess.run(["ntpq", "-c", "rv", server], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        # Check for the authenb variable
        if "authenb" in output.lower():
            for line in output.split("\n"):
                if "authenb" in line.lower():
                    # Extract the value of authenb
                    value = line.split('=')[-1].strip()
                    if value == "1":
                        return "Authentication enabled"
                    elif value == "0":
                        return "Authentication not enabled"
            return "authenb status unclear"
        return "No authentication information found"
    except Exception as e:
        return f"Error: {e}"

def check_nts_support(server, port=4460):
    try:
        # Attempt to establish a TLS connection for NTS
        context = ssl.create_default_context()
        with socket.create_connection((server, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=server) as ssock:
                return "NTS supported"
    except Exception as e:
        return "NTS not supported"

def process_ntp_authentication(input_csv, output_csv):
    results = []
    authenticated_count = 0
    unauthenticated_count = 0
    nts_supported_count = 0
    nts_not_supported_count = 0

    # Read input CSV file containing server list
    with open(input_csv, mode='r') as infile:
        reader = csv.reader(infile)
        servers = [row[0] for row in reader]

    for server in servers:
        print(f"Querying NTP Server: {server}")

        # Check for NTP authentication
        auth_info = check_ntp_authentication(server)
        print(f"Authentication Info: {auth_info}")

        # Check for NTS support
        nts_info = check_nts_support(server)
        print(f"NTS Info: {nts_info}")

        # Update counters
        if auth_info == "Authentication enabled":
            authenticated_count += 1
        elif auth_info == "Authentication not enabled":
            unauthenticated_count += 1
        
        if nts_info == "NTS supported":
            nts_supported_count += 1
        elif nts_info == "NTS not supported":
            nts_not_supported_count += 1

        results.append({"Server": server, "Authentication_Info": auth_info, "NTS_Info": nts_info})

    # Write results to output CSV file
    with open(output_csv, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["Server", "Authentication_Info", "NTS_Info"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {output_csv}")

    print(f"\nSummary")
    print(f"\Authenticated Servers: {authenticated_count}")
    print(f"Unauthenticated Servers: {unauthenticated_count}")
    print(f"NTS Supported Servers: {nts_supported_count}")
    print(f"NTS Not Supported Servers: {nts_not_supported_count}")

# Input and Output CSV paths
input_csv = "ntp_list.csv"  
output_csv = "ntp_authentication_and_nts.csv" 
process_ntp_authentication(input_csv, output_csv)
