import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load JSON files
data_files = [f for f in os.listdir('experiments') if f.endswith('.json')]
all_data = []

for file in data_files:
    with open(f'experiments2/{file}', 'r') as f:
        data = json.load(f)
        parts = file.split('_')
        user_id, trial_num, condition = parts[0][4:], int(parts[1][5:]), parts[2]

        final_point = data[-1]
        final_point.update({'user_id': user_id, 'trial_num': trial_num, 'condition': condition})
        all_data.append(final_point)

df = pd.DataFrame(all_data)

# Compute within-subject means (averaging over trials for each user in each condition)
df['trial_num'] = df['trial_num'].astype(int)
df['block_trial_num'] = df.groupby(['user_id', 'condition']).cumcount() + 1

# Aggregate by user and condition to get average performance per user per condition
df_grouped = df.groupby(['user_id', 'condition', 'block_trial_num'])[['score']].mean().reset_index()

# Learning curve visualization
plt.figure(figsize=(10, 6))
sns.lineplot(x='block_trial_num', y='score', hue='condition', data=df_grouped, marker='o', ci='sd')
plt.title('Learning Curve (Within Subjects)')
plt.xlabel('Trial Number')
plt.ylabel('Score')
plt.xticks(range(1, 6))
plt.grid()
plt.legend(title="Condition")
plt.show()
