import csv
import subprocess

def check_command(server, command):
    try:
        result = subprocess.run(["ntpq", "-c", command, server], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        if "unknown" in output.lower():
            return f"{command} not usable"
        return f"{command, output.lower()}"
    except Exception as e:
        return f"Error: {e}"

def get_ntp_features(server):
    try:
        # Check for 'version' command usability
        version_status = check_command(server, "version")
        # Check for 'monlist' command usability
        monlist_status = check_command(server, "monlist")
        # Check for 'rv' command usability
        rv_status = check_command(server, "rv")
        # Check for 'pe' command usability
        pe_status = check_command(server, "pe")
        # Check for 'mrulist' command usability
        mrulist_status = check_command(server, "mrulist")
        return {"Server": server, "Version Command": version_status, "Monlist Command": monlist_status, "rv Command": rv_status, "pe Command": pe_status, "Mrulist Command": mrulist_status}
    except Exception as e:
        return {"Server": server, "Version Command": f"Error: {e}", "Monlist Command": f"Error: {e}", "rv Command": f"Error: {e}", "pe Command": f"Error: {e}", "Mrulist Command": f"Error: {e}"}

def process_ntp_features(input_csv, output_csv):
    results = []

    with open(input_csv, mode='r') as infile:
        reader = csv.reader(infile)
        servers = [row[0] for row in reader]

    for server in servers:
        print(f"Querying NTP Server: {server}")
        features_info = get_ntp_features(server)
        results.append(features_info)
        print(f"Features Info: {features_info}")

    with open(output_csv, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["Server", "Version Command", "Monlist Command", "rv Command", "pe Command", "Mrulist Command"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {output_csv}")

# Input and Output CSV paths
input_csv = "ntp_list.csv"  
output_csv = "ntp_features.csv" 
process_ntp_features(input_csv, output_csv)
