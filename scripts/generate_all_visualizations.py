#!/usr/bin/env python3
"""
Generate All Visualizations for Chronos Paper
Creates all charts, graphs, and figures from the research
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

def create_output_dirs():
    """Create output directories for visualizations"""
    dirs = [
        'visualizations/performance',
        'visualizations/comparisons', 
        'visualizations/ablation',
        'visualizations/complexity',
        'visualizations/categories'
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def generate_main_performance_comparison():
    """Generate main performance comparison chart (Figure 1 in paper)"""
    
    # Data from paper
    models = ['Chronos', 'GPT-4.1', 'Claude-4\nOpus', 'Gemini-2.0\nPro']
    success_rates = [67.3, 13.8, 14.2, 15.0]
    colors = ['#2E7D32', '#1976D2', '#7B1FA2', '#F57C00']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(models, success_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate}%', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Add improvement annotations
    chronos_rate = success_rates[0]
    for i, (bar, rate) in enumerate(zip(bars[1:], success_rates[1:]), 1):
        improvement = chronos_rate / rate
        ax.annotate(f'{improvement:.1f}x',
                   xy=(bar.get_x() + bar.get_width()/2, rate),
                   xytext=(bar.get_x() + bar.get_width()/2, rate + 10),
                   ha='center', fontsize=10, color='red',
                   arrowprops=dict(arrowstyle='->', color='red', lw=1))
    
    ax.set_ylabel('Debug Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Debugging Performance Comparison\n5,000 Real-World Scenarios', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 80)
    
    # Add confidence intervals
    ci = [2.1, 1.2, 1.3, 1.5]
    for bar, rate, c in zip(bars, success_rates, ci):
        ax.errorbar(bar.get_x() + bar.get_width()/2, rate, yerr=c, 
                   fmt='none', color='black', capsize=5)
    
    # Add grid
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('visualizations/performance/main_comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig('visualizations/performance/main_comparison.pdf', bbox_inches='tight')
    print("✓ Generated main performance comparison")

def generate_category_performance():
    """Generate category-specific performance chart"""
    
    categories = ['Syntax\nErrors', 'Logic\nBugs', 'Concurrency\nIssues', 
                 'Memory\nProblems', 'API\nMisuse', 'Performance\nBugs']
    
    chronos = [94.2, 72.8, 58.3, 61.7, 79.1, 65.4]
    gpt4 = [82.3, 12.1, 3.2, 5.7, 18.9, 7.4]
    claude = [79.8, 10.7, 2.8, 4.3, 16.2, 6.1]
    gemini = [85.1, 15.3, 4.1, 6.9, 22.4, 9.8]
    
    x = np.arange(len(categories))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    bars1 = ax.bar(x - 1.5*width, chronos, width, label='Chronos', color='#2E7D32', alpha=0.8)
    bars2 = ax.bar(x - 0.5*width, gpt4, width, label='GPT-4.1', color='#1976D2', alpha=0.8)
    bars3 = ax.bar(x + 0.5*width, claude, width, label='Claude-4', color='#7B1FA2', alpha=0.8)
    bars4 = ax.bar(x + 1.5*width, gemini, width, label='Gemini-2.0', color='#F57C00', alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2, bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            if height > 5:  # Only show labels for visible bars
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Bug Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Performance by Bug Category', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('visualizations/categories/category_performance.png', dpi=300, bbox_inches='tight')
    print("✓ Generated category performance chart")

def generate_repository_scale_analysis():
    """Generate repository scale performance analysis"""
    
    scales = ['<10K LOC', '10K-100K', '100K-1M', '>1M LOC']
    chronos = [71.2, 68.9, 64.3, 59.7]
    baseline = [21.3, 14.7, 8.9, 3.8]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left plot: Absolute performance
    x = np.arange(len(scales))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, chronos, width, label='Chronos', color='#2E7D32', alpha=0.8)
    bars2 = ax1.bar(x + width/2, baseline, width, label='Best Baseline', color='#FF5722', alpha=0.8)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
    
    ax1.set_xlabel('Repository Size', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Performance vs Repository Scale', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scales)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Right plot: Improvement ratio
    improvements = [c/b for c, b in zip(chronos, baseline)]
    bars3 = ax2.bar(scales, improvements, color='#4CAF50', alpha=0.8)
    
    for bar, imp in zip(bars3, improvements):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{imp:.1f}x', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_xlabel('Repository Size', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Improvement Factor', fontsize=12, fontweight='bold')
    ax2.set_title('Chronos Advantage by Scale', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('visualizations/performance/repository_scale.png', dpi=300, bbox_inches='tight')
    print("✓ Generated repository scale analysis")

def generate_debugging_cycles_efficiency():
    """Generate debugging cycles efficiency chart"""
    
    iterations = ['1st Attempt', '2nd Attempt', '3rd Attempt', '4+ Attempts']
    chronos_cumulative = [42.3, 58.7, 65.3, 67.3]
    gpt4_cumulative = [3.2, 5.1, 6.8, 8.5]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(iterations))
    
    # Plot lines
    ax.plot(x, chronos_cumulative, 'o-', label='Chronos', color='#2E7D32', 
           linewidth=3, markersize=10, markeredgecolor='white', markeredgewidth=2)
    ax.plot(x, gpt4_cumulative, 's-', label='GPT-4.1', color='#1976D2',
           linewidth=2, markersize=8, markeredgecolor='white', markeredgewidth=2)
    
    # Fill areas
    ax.fill_between(x, chronos_cumulative, alpha=0.2, color='#2E7D32')
    ax.fill_between(x, gpt4_cumulative, alpha=0.2, color='#1976D2')
    
    # Add value labels
    for i, (c, g) in enumerate(zip(chronos_cumulative, gpt4_cumulative)):
        ax.text(i, c + 2, f'{c:.1f}%', ha='center', fontsize=10, fontweight='bold')
        ax.text(i, g + 2, f'{g:.1f}%', ha='center', fontsize=10)
    
    ax.set_xlabel('Fix Iteration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cumulative Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Debugging Cycle Efficiency\nIterative Refinement Performance', 
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(iterations)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 75)
    
    # Add convergence annotation
    ax.annotate('Converged', xy=(2.5, 65.3), xytext=(3.2, 55),
               arrowprops=dict(arrowstyle='->', color='green', lw=2),
               fontsize=11, color='green', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('visualizations/performance/debugging_cycles.png', dpi=300, bbox_inches='tight')
    print("✓ Generated debugging cycles efficiency chart")

def generate_retrieval_depth_analysis():
    """Generate AGR retrieval depth analysis"""
    
    k_values = ['k=1\n(Direct)', 'k=2\n(Expanded)', 'k=3\n(Deep)', 'k=adaptive\n(Dynamic)', 'Flat\nRetrieval']
    success_rates = [58.2, 72.4, 71.8, 87.1, 23.4]
    colors = ['#FFA726', '#FF7043', '#EF5350', '#4CAF50', '#BDBDBD']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(k_values, success_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Highlight best performance
    bars[3].set_edgecolor('#2E7D32')
    bars[3].set_linewidth(3)
    
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.set_xlabel('Retrieval Depth Strategy', fontsize=12, fontweight='bold')
    ax.set_ylabel('Debug Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Adaptive Graph-Guided Retrieval Performance\nO(k log d) Complexity Verification', 
                fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add complexity annotation
    ax.text(0.5, 0.95, 'Verified O(k log d) complexity with R²=0.89',
           transform=ax.transAxes, fontsize=11, ha='center',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('visualizations/complexity/retrieval_depth.png', dpi=300, bbox_inches='tight')
    print("✓ Generated retrieval depth analysis")

def generate_ablation_study():
    """Generate ablation study results"""
    
    components = ['Full\nChronos', 'No Multi-Code\nAssociation', 'Static Memory\nOnly',
                 'No Orchestration\nLoop', 'No AGR\n(Flat Retrieval)']
    success_rates = [65.3, 35.8, 40.1, 42.5, 28.7]
    impacts = [0, -45, -39, -35, -56]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Success rates
    colors = ['#2E7D32'] + ['#EF5350'] * 4
    bars1 = ax1.bar(components, success_rates, color=colors, alpha=0.8, edgecolor='black')
    
    for bar, rate in zip(bars1, success_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    ax1.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Ablation Study Results', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, 75)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.tick_params(axis='x', rotation=15)
    
    # Right: Impact analysis
    colors2 = ['#4CAF50'] + ['#F44336'] * 4
    bars2 = ax2.bar(components, impacts, color=colors2, alpha=0.8, edgecolor='black')
    
    for bar, impact in zip(bars2, impacts):
        if impact < 0:
            va = 'top'
            y_offset = -2
        else:
            va = 'bottom'
            y_offset = 2
        ax2.text(bar.get_x() + bar.get_width()/2., impact + y_offset,
                f'{impact}%', ha='center', va=va, fontweight='bold')
    
    ax2.set_ylabel('Performance Impact (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Component Contribution Analysis', fontsize=13, fontweight='bold')
    ax2.axhline(y=0, color='black', linewidth=1)
    ax2.set_ylim(-65, 10)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    plt.savefig('visualizations/ablation/ablation_study.png', dpi=300, bbox_inches='tight')
    print("✓ Generated ablation study")

def generate_token_efficiency():
    """Generate token efficiency visualization"""
    
    models = ['Chronos', 'GPT-4.1', 'Claude-4', 'Gemini-2.0']
    input_tokens = [3600, 8500, 7200, 9800]
    output_tokens = [3000, 1200, 1500, 1800]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Token distribution
    x = np.arange(len(models))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, input_tokens, width, label='Input Tokens', color='#2196F3', alpha=0.8)
    bars2 = ax1.bar(x + width/2, output_tokens, width, label='Output Tokens', color='#FF9800', alpha=0.8)
    
    ax1.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Tokens', fontsize=12, fontweight='bold')
    ax1.set_title('Token Usage Comparison', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Right: Output efficiency
    output_ratios = [o/i for o, i in zip(output_tokens, input_tokens)]
    colors = ['#4CAF50', '#FFC107', '#FF5722', '#9C27B0']
    bars3 = ax2.bar(models, output_ratios, color=colors, alpha=0.8)
    
    for bar, ratio in zip(bars3, output_ratios):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{ratio:.1%}', ha='center', va='bottom', fontweight='bold')
    
    ax2.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Output/Input Ratio', fontsize=12, fontweight='bold')
    ax2.set_title('Output Generation Efficiency\n(Higher is better for debugging)', 
                 fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 1.0)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add annotation
    ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
    ax2.text(0.5, 0.52, 'Optimal for debugging', ha='center', fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('visualizations/performance/token_efficiency.png', dpi=300, bbox_inches='tight')
    print("✓ Generated token efficiency chart")

def generate_cost_comparison():
    """Generate cost per fix comparison"""
    
    models = ['Chronos', 'GPT-4.1', 'Claude-4\nOpus', 'Gemini-2.0\nPro']
    costs = [1.36, 5.53, 4.89, 4.25]
    colors = ['#4CAF50', '#2196F3', '#9C27B0', '#FF9800']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(models, costs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar, cost in zip(bars, costs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'${cost:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Add savings annotations
    chronos_cost = costs[0]
    for i, (bar, cost) in enumerate(zip(bars[1:], costs[1:]), 1):
        savings = ((cost - chronos_cost) / cost) * 100
        ax.text(bar.get_x() + bar.get_width()/2., 1,
                f'{savings:.0f}% savings', ha='center', fontsize=10,
                color='green', fontweight='bold')
    
    ax.set_ylabel('Cost per Successful Fix ($)', fontsize=12, fontweight='bold')
    ax.set_title('Economic Efficiency Comparison\nCost per Successful Debug Fix', 
                fontsize=14, fontweight='bold')
    ax.set_ylim(0, 6.5)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add total cost annotation for 1000 bugs
    ax.text(0.5, 0.95, 'For 1,000 bugs: Chronos saves ~$4,000 vs GPT-4.1',
           transform=ax.transAxes, ha='center', fontsize=11,
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('visualizations/comparisons/cost_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Generated cost comparison")

def generate_language_performance():
    """Generate language-specific performance comparison"""
    
    languages = ['Python', 'JavaScript', 'Java', 'Go', 'C++']
    chronos = [68.7, 64.2, 63.9, 66.8, 61.2]
    gpt4 = [11.2, 7.8, 6.3, 9.1, 5.2]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(languages))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, chronos, width, label='Chronos', color='#2E7D32', alpha=0.8)
    bars2 = ax.bar(x + width/2, gpt4, width, label='GPT-4.1', color='#1976D2', alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
    
    # Add improvement factors
    for i, (c, g) in enumerate(zip(chronos, gpt4)):
        improvement = c / g
        ax.text(i, max(c, g) + 5, f'{improvement:.1f}x',
               ha='center', fontsize=10, color='red', fontweight='bold')
    
    ax.set_xlabel('Programming Language', fontsize=12, fontweight='bold')
    ax.set_ylabel('Debug Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Performance Across Programming Languages', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(languages)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 80)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('visualizations/performance/language_performance.png', dpi=300, bbox_inches='tight')
    print("✓ Generated language performance comparison")

def generate_memory_impact():
    """Generate persistent memory impact visualization"""
    
    sessions = np.arange(0, 101, 10)
    success_rate = [35, 42, 48, 52, 56, 59, 61, 63, 64, 65, 65]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(sessions, success_rate, 'o-', color='#2E7D32', linewidth=3,
           markersize=10, markeredgecolor='white', markeredgewidth=2)
    
    ax.fill_between(sessions, success_rate, alpha=0.2, color='#2E7D32')
    
    # Add trend line
    z = np.polyfit(sessions, success_rate, 2)
    p = np.poly1d(z)
    x_smooth = np.linspace(0, 100, 100)
    ax.plot(x_smooth, p(x_smooth), '--', color='red', alpha=0.5, label='Trend')
    
    ax.set_xlabel('Debugging Sessions', fontsize=12, fontweight='bold')
    ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Persistent Debug Memory Learning Curve\nRepository-Specific Improvement Over Time',
                fontsize=14, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.set_ylim(30, 70)
    ax.grid(True, alpha=0.3)
    
    # Add annotations
    ax.annotate('Initial Performance', xy=(0, 35), xytext=(10, 30),
               arrowprops=dict(arrowstyle='->', color='blue'),
               fontsize=11, color='blue')
    
    ax.annotate('Converged Performance', xy=(100, 65), xytext=(70, 68),
               arrowprops=dict(arrowstyle='->', color='green'),
               fontsize=11, color='green')
    
    ax.text(50, 55, '86% improvement\nthrough learning', ha='center',
           fontsize=11, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('visualizations/performance/memory_impact.png', dpi=300, bbox_inches='tight')
    print("✓ Generated memory impact visualization")

def generate_comprehensive_dashboard():
    """Generate comprehensive performance dashboard"""
    
    fig = plt.figure(figsize=(16, 12))
    
    # Create grid
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Overall Performance (top left, 2x1)
    ax1 = fig.add_subplot(gs[0, :2])
    models = ['Chronos', 'GPT-4.1', 'Claude-4', 'Gemini-2.0']
    metrics = {
        'Success Rate': [67.3, 13.8, 14.2, 15.0],
        'Root Cause': [89.0, 12.3, 11.7, 15.8],
        'Precision': [92.0, 68.0, 67.0, 74.0]
    }
    
    x = np.arange(len(models))
    width = 0.25
    colors = ['#2E7D32', '#FF6B6B', '#4ECDC4']
    
    for i, (metric, values) in enumerate(metrics.items()):
        offset = (i - 1) * width
        bars = ax1.bar(x + offset, values, width, label=metric, color=colors[i], alpha=0.8)
        for bar in bars:
            height = bar.get_height()
            if height > 20:
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.0f}', ha='center', va='bottom', fontsize=8)
    
    ax1.set_xlabel('Model')
    ax1.set_ylabel('Performance (%)')
    ax1.set_title('Comprehensive Performance Metrics', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. Cost Efficiency (top right)
    ax2 = fig.add_subplot(gs[0, 2])
    costs = [1.36, 5.53, 4.89, 4.25]
    colors2 = ['#4CAF50', '#FF5252', '#FF5252', '#FF5252']
    ax2.bar(models, costs, color=colors2, alpha=0.8)
    ax2.set_ylabel('Cost per Fix ($)')
    ax2.set_title('Economic Efficiency', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Category Performance (middle left, 2x1)
    ax3 = fig.add_subplot(gs[1, :2])
    categories = ['Syntax', 'Logic', 'Concur.', 'Memory', 'API', 'Perf.']
    chronos_cat = [94.2, 72.8, 58.3, 61.7, 79.1, 65.4]
    baseline_cat = [82.3, 12.1, 3.2, 5.7, 18.9, 7.4]
    
    x = np.arange(len(categories))
    width = 0.35
    ax3.bar(x - width/2, chronos_cat, width, label='Chronos', color='#2E7D32', alpha=0.8)
    ax3.bar(x + width/2, baseline_cat, width, label='Best Baseline', color='#FF6B6B', alpha=0.8)
    ax3.set_xlabel('Bug Category')
    ax3.set_ylabel('Success Rate (%)')
    ax3.set_title('Category-Specific Performance', fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(categories)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Iterations (middle right)
    ax4 = fig.add_subplot(gs[1, 2])
    iterations = [7.8, 6.5, 6.2, 5.8]
    colors3 = ['#4CAF50', '#FFC107', '#FFC107', '#FFC107']
    ax4.bar(models, iterations, color=colors3, alpha=0.8)
    ax4.set_ylabel('Average Iterations')
    ax4.set_title('Fix Iterations', fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Scale Performance (bottom left)
    ax5 = fig.add_subplot(gs[2, 0])
    scales = ['<10K', '10-100K', '100K-1M', '>1M']
    chronos_scale = [71.2, 68.9, 64.3, 59.7]
    ax5.plot(scales, chronos_scale, 'o-', color='#2E7D32', linewidth=2, markersize=8)
    ax5.set_xlabel('Repository Size (LOC)')
    ax5.set_ylabel('Success Rate (%)')
    ax5.set_title('Scale Performance', fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. Learning Curve (bottom middle)
    ax6 = fig.add_subplot(gs[2, 1])
    sessions = [0, 20, 40, 60, 80, 100]
    learning = [35, 48, 56, 61, 64, 65]
    ax6.plot(sessions, learning, 'o-', color='#9C27B0', linewidth=2, markersize=8)
    ax6.fill_between(sessions, learning, alpha=0.2, color='#9C27B0')
    ax6.set_xlabel('Sessions')
    ax6.set_ylabel('Success Rate (%)')
    ax6.set_title('PDM Learning Curve', fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # 7. Statistical Significance (bottom right)
    ax7 = fig.add_subplot(gs[2, 2])
    effect_sizes = [3.87, 2.45, 2.89]
    comparisons = ['vs GPT-4.1', 'vs Claude-4', 'vs Gemini-2.0']
    colors4 = ['#4CAF50', '#4CAF50', '#4CAF50']
    bars = ax7.barh(comparisons, effect_sizes, color=colors4, alpha=0.8)
    ax7.set_xlabel("Cohen's d Effect Size")
    ax7.set_title('Statistical Significance', fontweight='bold')
    ax7.axvline(x=2, color='red', linestyle='--', alpha=0.5)
    ax7.text(2.1, 0.5, 'Large Effect', fontsize=9, color='red')
    ax7.grid(True, alpha=0.3, axis='x')
    
    # Main title
    fig.suptitle('Kodezi Chronos - Comprehensive Performance Dashboard', 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig('visualizations/performance/comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
    plt.savefig('visualizations/performance/comprehensive_dashboard.pdf', bbox_inches='tight')
    print("✓ Generated comprehensive dashboard")

def main():
    """Generate all visualizations"""
    print("Generating Chronos Visualizations")
    print("=" * 50)
    
    # Create output directories
    create_output_dirs()
    
    # Generate all charts
    generate_main_performance_comparison()
    generate_category_performance()
    generate_repository_scale_analysis()
    generate_debugging_cycles_efficiency()
    generate_retrieval_depth_analysis()
    generate_ablation_study()
    generate_token_efficiency()
    generate_cost_comparison()
    generate_language_performance()
    generate_memory_impact()
    generate_comprehensive_dashboard()
    
    print("\n" + "=" * 50)
    print("✓ All visualizations generated successfully!")
    print("Location: visualizations/")
    
    # Generate summary
    summary = {
        'generated': datetime.now().isoformat(),
        'charts': [
            'main_comparison',
            'category_performance',
            'repository_scale',
            'debugging_cycles',
            'retrieval_depth',
            'ablation_study',
            'token_efficiency',
            'cost_comparison',
            'language_performance',
            'memory_impact',
            'comprehensive_dashboard'
        ],
        'formats': ['png', 'pdf'],
        'total_charts': 11
    }
    
    with open('visualizations/generation_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nGenerated {summary['total_charts']} visualizations")
    print("Formats: PNG (300 DPI) and PDF")

if __name__ == "__main__":
    main()