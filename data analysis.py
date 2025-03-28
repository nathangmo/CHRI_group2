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
    with open(f'experiments2/{file}', 'r') as f:
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

# One-way ANOVA
f_val, p_val = stats.f_oneway(baseline_times, constant_times, dynamic_times)
print(f"ANOVA results for completion time: F={f_val:.2f}, p={p_val:.4f}")

# If significant, do post-hoc tests
if p_val < 0.05:
    print("\nPost-hoc Tukey HSD tests:")
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    tukey = pairwise_tukeyhsd(endog=df['completion_time'],
                             groups=df['condition'],
                             alpha=0.05)
    print(tukey)

# Create contingency table of condition vs success
contingency_table = pd.crosstab(df['condition'], df['success'])

# Chi-square test
chi2, p, dof, expected = stats.chi2_contingency(contingency_table)
print(f"\nChi-square test for success rate: χ²={chi2:.2f}, p={p:.4f}")

plt.figure(figsize=(10, 6))
sns.boxplot(x='condition', y='completion_time', data=df)
plt.title('Completion Time by Force Assist Type')
plt.ylabel('Time (seconds)')
plt.xlabel('Force Assist Type')
plt.savefig('completion_time_by_condition.png')
plt.show()

success_rates = df.groupby('condition')['success'].mean()

plt.figure(figsize=(8, 5))
success_rates.plot(kind='bar')
plt.title('Success Rate by Force Assist Type')
plt.ylabel('Success Rate')
plt.ylim(0, 1)
plt.savefig('success_rate_by_condition.png')
plt.show()


def plot_force_profiles(user_id, trial_num):
    """Plot force components over time for a specific trial"""
    filename = f"experiments/user{user_id}_trial{trial_num}_*_data_*.json"
    matching_files = [f for f in data_files if f.startswith(f"user{user_id}_trial{trial_num}")]

    if not matching_files:
        print(f"No data found for user {user_id} trial {trial_num}")
        return

    with open(f'experiments/{matching_files[0]}', 'r') as f:
        trial_data = json.load(f)

    times = [d['time'] for d in trial_data]
    forces = [d['Force'] for d in trial_data]
    fx = [f[0] for f in forces]
    fy = [f[1] for f in forces]

    plt.figure(figsize=(12, 6))
    plt.plot(times, fx, label='Force X')
    plt.plot(times, fy, label='Force Y')
    plt.title(f'Force Profile - User {user_id} Trial {trial_num}')
    plt.xlabel('Time (s)')
    plt.ylabel('Force (N)')
    plt.legend()
    plt.grid()
    plt.savefig(f'force_profile_user{user_id}_trial{trial_num}.png')
    plt.show()

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

# ANOVA results
print("\nONE-WAY ANOVA FOR COMPLETION TIME")
print("-"*50)
print(f"F-value: {f_val:.2f}")
print(f"p-value: {p_val:.4f}")


# Calculate accuracy metrics
print("=" * 80)
print("SCORE/ACCURACY ANALYSIS")
print("=" * 80)

# Basic descriptive stats
score_stats = df.groupby('condition')['score'].describe()
print("\nBasic Score Statistics:")
print(score_stats)

# Normalize scores if needed (assuming max possible score is 100)
df['accuracy'] = df['score'] / 100

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

# ANOVA
f_val, p_val = stats.f_oneway(baseline_scores, constant_scores, dynamic_scores)
print(f"\nANOVA for Accuracy Scores: F={f_val:.2f}, p={p_val:.4f}")

# Post-hoc tests if ANOVA significant
if p_val < 0.05:
    print("\nPost-hoc Tukey HSD tests:")
    tukey = pairwise_tukeyhsd(endog=df['score'],
                              groups=df['condition'],
                              alpha=0.05)
    print(tukey)

# Effect sizes
print("\nEffect Sizes (Cohen's d):")


def cohens_d(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(
        ((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof)


print(f"Baseline vs Constant: d={cohens_d(baseline_scores, constant_scores):.2f}")
print(f"Baseline vs Dynamic: d={cohens_d(baseline_scores, dynamic_scores):.2f}")
print(f"Constant vs Dynamic: d={cohens_d(constant_scores, dynamic_scores):.2f}")

# Correlation between time and accuracy
corr, p_corr = stats.pearsonr(df['completion_time'], df['score'])
print(f"\nCorrelation between completion time and accuracy: r={corr:.2f}, p={p_corr:.4f}")


# Create combined performance metric (lower is better)
df['performance_index'] = df['completion_time'] / df['score'] * 1000

print("\n" + "="*80)
print("COMBINED PERFORMANCE ANALYSIS")
print("="*80)
print(df.groupby('condition')['performance_index'].describe())

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

# Find outlier threshold (3 standard deviations)
outliers = df[df['time_zscore'] > 3]
print("Potential outliers detected:")
print(outliers[['user_id', 'trial_num', 'condition', 'completion_time', 'score']])