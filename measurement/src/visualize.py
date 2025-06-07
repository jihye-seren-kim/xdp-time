import pandas as pd
import matplotlib.pyplot as plt

files = {
    10: 'rate_limiting_results_qps_10.csv',
    20: 'rate_limiting_results_qps_20.csv',
    50: 'rate_limiting_results_qps_50.csv',
    100: 'rate_limiting_results_qps_100.csv'
}

all_data = []

for qps, filepath in files.items():
    df = pd.read_csv(filepath)
    grouped = df.groupby('Server').agg({'Successful Requests': 'mean'}).reset_index()
    grouped['QPS'] = qps
    all_data.append(grouped)

combined_df = pd.concat(all_data)

plt.figure(figsize=(10,6))
combined_df.boxplot(column='Successful Requests', by='QPS')
plt.title('Distribution of Average Successful Requests per Server by QPS', fontsize=16)
plt.suptitle('')
plt.xlabel('QPS', fontsize=14)
plt.ylabel('Average Successful Requests', fontsize=14)
plt.show()
