import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns

# Load all JSON files from experiments directory
data_files = [f for f in os.listdir('experiments') if f.endswith('.json')]

all_data = []
for file in data_files:
    with open(f'experiments/{file}', 'r') as f:
        data = json.load(f)
        # Extract metadata from filename
        parts = file.split('_')
        user_id = parts[0][4:]  # Extract user number from 'userX'
        trial_num = parts[1][5:]  # Extract trial number from 'trialX'
        condition = parts[2]  # Condition is the third part

        # Get the last data point which contains final results
        final_point = data[-1]
        final_point['user_id'] = user_id
        final_point['trial_num'] = trial_num
        final_point['condition'] = condition

        # Calculate additional metrics
        final_point['completion_time'] = final_point['time']
        final_point['success'] = 1 if final_point['score'] > 0 else 0

        all_data.append(final_point)

# Create DataFrame
df = pd.DataFrame(all_data)

# Summary statistics by condition
summary_stats = df.groupby('condition').agg({
    'completion_time': ['mean', 'std', 'median'],
    'score': ['mean', 'std', 'median'],
    'success': 'mean',
    'shocks': ['mean', 'std']
})

print(summary_stats)

# Separate data by condition
baseline_times = df[df['condition'] == 'baseline']['completion_time']
constant_times = df[df['condition'] == 'constant']['completion_time']
dynamic_times = df[df['condition'] == 'dynamic']['completion_time']

# Print descriptive statistics with clear formatting
print("="*80)
print("DESCRIPTIVE STATISTICS BY CONDITION")
print("="*80)
print(f"{'Condition':<10} {'Mean Time':>12} {'Std Time':>12} {'Median Time':>12} "
      f"{'Success Rate':>12} {'Mean Shocks':>12} {'Std Shocks':>12}")
print("-"*80)

for condition in ['baseline', 'constant', 'dynamic']:
    cond_data = df[df['condition'] == condition]
    print(f"{condition:<10} {cond_data['completion_time'].mean():>12.2f} "
          f"{cond_data['completion_time'].std():>12.2f} "
          f"{cond_data['completion_time'].median():>12.2f} "
          f"{cond_data['success'].mean():>12.2f} "
          f"{cond_data['shocks'].mean():>12.2f} "
          f"{cond_data['shocks'].std():>12.2f}")

print("\n" + "="*80)
print("STATISTICAL TEST RESULTS")
print("="*80)

# Calculate accuracy metrics
print("=" * 80)
print("SCORE/ACCURACY ANALYSIS")
print("=" * 80)
# Correlation between accuracy (score) and completion time
corr, p_corr = stats.pearsonr(df['completion_time'], df['score'])
print("=" * 80)
print("SCORE (ACCURACY) VS. COMPLETION TIME ANALYSIS")
print("=" * 80)
print(f"Pearson correlation: r={corr:.2f}, p={p_corr:.4f}")

# Linear regression model for Score vs. Completion Time
slope, intercept, r_value, p_value, std_err = stats.linregress(df['completion_time'], df['score'])
print(f"Regression Model: Score = {slope:.2f} * Time + {intercept:.2f}")
print(f"R-squared: {r_value**2:.3f}, p-value: {p_value:.4f}")

# Scatter plot with regression line, color-coded by condition
plt.figure(figsize=(12, 6))
sns.set_style("whitegrid")
palette = {'baseline': '#1f77b4', 'constant': '#ff7f0e', 'dynamic': '#2ca02c'}

# Plot scatter with regression lines per condition
sns.lmplot(x='completion_time',
           y='score',
           hue='condition',  # Color by condition
           data=df,
           palette=palette,
           height=6,
           aspect=1.5,
           scatter_kws={'alpha': 0.7, 's': 80},
           line_kws={'linewidth': 2})

# Customize plot
plt.xlabel("Completion Time (seconds)", fontsize=14)
plt.ylabel("Score (Accuracy)", fontsize=14)
plt.title("Score vs. Completion Time (Color-Coded by Condition)", fontsize=16)
plt.grid(alpha=0.3)

# Save and Show
plt.savefig("score_vs_time_colored.png", dpi=300)
plt.show()

# Basic descriptive stats
score_stats = df.groupby('condition')['score'].describe()
print("\nBasic Score Statistics:")
print(score_stats)

# Normalize scores if needed (assuming max possible score is 300)
df['accuracy'] = df['score'] / 300

# Visualization
plt.figure(figsize=(12, 6))
sns.boxplot(x='condition', y='score', data=df)
plt.title('Accuracy Scores by Condition')
plt.ylabel('Score (Accuracy)')
plt.xlabel('Force Assist Type')
plt.savefig('accuracy_scores.png', dpi=300)
plt.show()

# Statistical tests
print("\nStatistical Comparisons:")
baseline_scores = df[df['condition'] == 'baseline']['score']
constant_scores = df[df['condition'] == 'constant']['score']
dynamic_scores = df[df['condition'] == 'dynamic']['score']


# Correlation between time and accuracy
corr, p_corr = stats.pearsonr(df['completion_time'], df['score'])
print(f"\nCorrelation between completion time and accuracy: r={corr:.2f}, p={p_corr:.4f}")


'''
Learning Curves
'''
# First, create a relative trial number (1-5) within each condition block
df['block_trial_num'] = df.groupby(['user_id', 'condition']).cumcount() + 1

# Set up the plot
plt.figure(figsize=(12, 8))
sns.set_style("whitegrid")
palette = {'baseline': '#1f77b4', 'constant': '#ff7f0e', 'dynamic': '#2ca02c'}

# Create main scatter plot
scatter = sns.lmplot(x='block_trial_num',
                     y='score',
                     hue='condition',
                     data=df,
                     palette=palette,
                     height=8,
                     aspect=1.5,
                     scatter_kws={'s': 100, 'alpha': 0.7},
                     line_kws={'lw': 3},
                     ci=95,
                     x_jitter=0.1,
                     y_jitter=0.1)

# Add individual user trajectories
for user_id in df['user_id'].unique():
    user_data = df[df['user_id'] == user_id]
    for condition, color in palette.items():
        cond_data = user_data[user_data['condition'] == condition]
        if not cond_data.empty:
            plt.plot(cond_data['block_trial_num'],
                    cond_data['score'],
                    color=color,
                    alpha=0.15,
                    linestyle='--',
                    linewidth=1)

# Add condition averages
for condition, color in palette.items():
    cond_avg = df[df['condition'] == condition].groupby('block_trial_num')['score'].mean()
    plt.plot(cond_avg.index,
            cond_avg.values,
            color=color,
            linewidth=4,
            marker='o',
            markersize=10,
            label=f'{condition} (avg)')

# Customize plot
plt.title('Learning Curves Within Condition Blocks (Trials 1-5)', fontsize=16, pad=20)
plt.xlabel('Trial Number Within Condition Block', fontsize=14)
plt.ylabel('Accuracy Score', fontsize=14)
plt.xticks(np.arange(1, 6, 1))
plt.xlim(0.5, 5.5)
plt.grid(True, alpha=0.3)

# Add legend
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles[-3:], labels[-3:],
          title='Condition Averages',
          bbox_to_anchor=(1.05, 1),
          loc='upper left')

plt.tight_layout()
plt.savefig('learning_curves_within_blocks.png', dpi=300, bbox_inches='tight')
plt.show()

# Calculate z-scores for completion times
df['time_zscore'] = np.abs(stats.zscore(df['completion_time']))

# # Find outlier threshold (3 standard deviations)
# outliers = df[df['time_zscore'] > 3]
# print("Potential outliers detected:")
# print(outliers[['user_id', 'trial_num', 'condition', 'completion_time', 'score']])
#
