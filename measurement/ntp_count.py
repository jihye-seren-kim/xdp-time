import pandas as pd
import ace_tools as tools

data = pd.read_csv(ntp_list.csv)
df = pd.DataFrame(data)

# Calculate counts for each unique value in the relevant columns
version_counts = df["Version"].value_counts().reset_index()
version_counts.columns = ["Version", "Version_Count"]

stratum_counts = df["Stratum"].value_counts().reset_index()
stratum_counts.columns = ["Stratum", "Stratum_Count"]

mode_counts = df["Mode"].value_counts().reset_index()
mode_counts.columns = ["Mode", "Mode_Count"]

# Merge all counts into a single DataFrame for display
merged_counts = pd.DataFrame({
    "Version": version_counts["Version"],
    "Version_Count": version_counts["Version_Count"],
    "Stratum": stratum_counts["Stratum"],
    "Stratum_Count": stratum_counts["Stratum_Count"],
    "Mode": mode_counts["Mode"],
    "Mode_Count": mode_counts["Mode_Count"],
})

# Display the merged table
print(merged_counts)
