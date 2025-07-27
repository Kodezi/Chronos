#!/usr/bin/env python3
"""
Generate visualizations for Kodezi Chronos research results.

This script creates various charts and graphs to visualize the performance
metrics and evaluation results of Chronos compared to baseline models.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "results" / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)


def create_overall_performance_comparison():
    """Create bar chart comparing overall debugging success rates."""
    models = ['GPT-4', 'Claude-3', 'Gemini-1.5', 'Chronos']
    success_rates = [8.5, 7.8, 11.2, 65.3]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(models, success_rates, color=colors, alpha=0.8)
    
    # Add value labels on bars
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Debugging Success Rate (%)', fontsize=12)
    ax.set_title('Overall Debugging Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 75)
    
    # Add 6-7x improvement annotation
    ax.annotate('6-7x improvement', xy=(3, 65.3), xytext=(2.5, 55),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'overall_performance.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_bug_category_heatmap():
    """Create heatmap showing performance across bug categories."""
    categories = ['Syntax', 'Logic', 'Concurrency', 'Memory', 'API', 'Performance']
    models = ['GPT-4', 'Claude-3', 'Gemini-1.5', 'Chronos']
    
    # Performance data (from the paper)
    data = np.array([
        [82.3, 12.1, 3.2, 5.7, 18.9, 7.4],    # GPT-4
        [79.8, 10.7, 2.8, 4.3, 16.2, 6.1],    # Claude-3
        [85.1, 15.3, 4.1, 6.9, 22.4, 9.8],    # Gemini-1.5
        [94.2, 72.8, 58.3, 61.7, 79.1, 65.4]  # Chronos
    ])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create heatmap
    im = ax.imshow(data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
    
    # Set ticks
    ax.set_xticks(np.arange(len(categories)))
    ax.set_yticks(np.arange(len(models)))
    ax.set_xticklabels(categories)
    ax.set_yticklabels(models)
    
    # Rotate the tick labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Success Rate (%)', rotation=270, labelpad=20)
    
    # Add text annotations
    for i in range(len(models)):
        for j in range(len(categories)):
            text = ax.text(j, i, f'{data[i, j]:.1f}%',
                          ha="center", va="center", color="black" if data[i, j] < 50 else "white",
                          fontsize=10)
    
    ax.set_title('Debugging Success Rate by Bug Category', fontsize=14, fontweight='bold')
    fig.tight_layout()
    plt.savefig(OUTPUT_DIR / 'bug_category_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_ablation_study_chart():
    """Create chart showing impact of removing components."""
    components = ['Full\nChronos', 'No Multi-Code\nAssociation', 'Static Memory\nOnly', 
                  'No Orchestration\nLoop', 'No AGR', 'No Pattern\nLearning']
    success_rates = [90.0, 49.0, 62.0, 55.0, 41.0, 58.0]
    colors = ['#96CEB4', '#FF6B6B', '#FFA07A', '#FFB347', '#FF6B6B', '#FFA07A']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(components, success_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Highlight full Chronos
    bars[0].set_edgecolor('green')
    bars[0].set_linewidth(3)
    
    # Add value labels
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate}%', ha='center', va='bottom', fontsize=11)
    
    # Add impact annotations
    baseline = success_rates[0]
    for i, (bar, rate) in enumerate(zip(bars[1:], success_rates[1:]), 1):
        impact = ((rate - baseline) / baseline) * 100
        ax.text(bar.get_x() + bar.get_width()/2., 5,
                f'{impact:+.1f}%', ha='center', va='bottom', 
                fontsize=10, color='red', fontweight='bold')
    
    ax.set_ylabel('Debugging Success Rate (%)', fontsize=12)
    ax.set_title('Ablation Study: Component Impact Analysis', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.axhline(y=baseline, color='green', linestyle='--', alpha=0.5, label='Full Chronos baseline')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'ablation_study.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_debugging_cycles_distribution():
    """Create histogram showing distribution of debugging cycles needed."""
    # Data based on paper statistics
    cycles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    chronos_dist = [45.2, 31.6, 15.3, 5.2, 1.6, 0.7, 0.3, 0.1, 0, 0]
    gpt4_dist = [8.5, 12.3, 15.2, 18.1, 16.4, 12.3, 8.7, 5.2, 2.3, 1.0]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Chronos distribution
    ax1.bar(cycles, chronos_dist, color='#96CEB4', alpha=0.8, edgecolor='black')
    ax1.set_xlabel('Number of Debugging Cycles', fontsize=12)
    ax1.set_ylabel('Success Rate (%)', fontsize=12)
    ax1.set_title('Chronos: Debugging Cycles Distribution', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, 50)
    
    # Add cumulative line
    cumulative = np.cumsum(chronos_dist)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(cycles, cumulative, 'r-', marker='o', linewidth=2, markersize=6)
    ax1_twin.set_ylabel('Cumulative Success Rate (%)', fontsize=12, color='red')
    ax1_twin.set_ylim(0, 100)
    ax1_twin.tick_params(axis='y', labelcolor='red')
    
    # GPT-4 distribution (for comparison)
    ax2.bar(cycles, gpt4_dist, color='#FF6B6B', alpha=0.8, edgecolor='black')
    ax2.set_xlabel('Number of Debugging Cycles', fontsize=12)
    ax2.set_ylabel('Success Rate (%)', fontsize=12)
    ax2.set_title('GPT-4: Debugging Cycles Distribution', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 50)
    
    # Add text showing total success
    ax1.text(0.95, 0.95, f'Total: {sum(chronos_dist):.1f}%', 
             transform=ax1.transAxes, ha='right', va='top', 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax2.text(0.95, 0.95, f'Total: {sum(gpt4_dist):.1f}%', 
             transform=ax2.transAxes, ha='right', va='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'debugging_cycles.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_retrieval_performance_chart():
    """Create chart comparing retrieval methods."""
    methods = ['k=1', 'k=2', 'k=3', 'k=adaptive', 'Flat']
    precision = [84.3, 91.2, 88.7, 92.8, 71.4]
    recall = [72.1, 86.4, 89.2, 90.3, 68.2]
    debug_success = [58.2, 72.4, 71.8, 87.1, 23.4]
    
    x = np.arange(len(methods))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars1 = ax.bar(x - width, precision, width, label='Precision', color='#4ECDC4', alpha=0.8)
    bars2 = ax.bar(x, recall, width, label='Recall', color='#45B7D1', alpha=0.8)
    bars3 = ax.bar(x + width, debug_success, width, label='Debug Success', color='#96CEB4', alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Retrieval Method', fontsize=12)
    ax.set_ylabel('Performance (%)', fontsize=12)
    ax.set_title('Adaptive Graph-Guided Retrieval Performance', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.legend()
    ax.set_ylim(0, 105)
    
    # Highlight adaptive
    ax.axvspan(2.5, 3.5, alpha=0.1, color='green')
    ax.text(3, 95, 'Optimal', ha='center', fontsize=11, fontweight='bold', color='green')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'retrieval_performance.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_cost_analysis_chart():
    """Create cost-effectiveness analysis chart."""
    models = ['GPT-4', 'Claude-3', 'Gemini-1.5', 'Chronos', 'Human Dev']
    cost_per_attempt = [0.47, 0.52, 0.68, 0.89, 180]
    success_rate = [8.5, 7.8, 11.2, 65.3, 94.2]
    effective_cost = [5.53, 6.67, 6.07, 1.36, 191]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Cost per attempt
    bars1 = ax1.bar(models, cost_per_attempt, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#DDA0DD'])
    ax1.set_ylabel('Cost per Attempt ($)', fontsize=12)
    ax1.set_title('Cost per Debugging Attempt', fontsize=13, fontweight='bold')
    ax1.set_yscale('log')
    
    # Add value labels
    for bar, cost in zip(bars1, cost_per_attempt):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                f'${cost}', ha='center', va='bottom', fontsize=10)
    
    # Effective cost (cost / success rate)
    bars2 = ax2.bar(models, effective_cost, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#DDA0DD'])
    ax2.set_ylabel('Effective Cost per Success ($)', fontsize=12)
    ax2.set_title('Cost per Successful Debug (Lower is Better)', fontsize=13, fontweight='bold')
    ax2.set_yscale('log')
    
    # Add value labels
    for bar, cost in zip(bars2, effective_cost):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                f'${cost:.2f}', ha='center', va='bottom', fontsize=10)
    
    # Highlight Chronos's advantage
    ax2.axhspan(0.1, 2, alpha=0.1, color='green')
    ax2.text(3, 0.5, 'Most Cost-Effective', ha='center', fontsize=11, 
             fontweight='bold', color='green', rotation=0)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'cost_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()


def create_summary_infographic():
    """Create a summary infographic with key metrics."""
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle('Kodezi Chronos: Key Performance Metrics', fontsize=20, fontweight='bold')
    
    # Remove axes
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Key metrics boxes
    metrics = [
        {'title': 'Debug Success', 'value': '65.3%', 'comparison': '7.7x vs GPT-4', 'pos': (2, 7)},
        {'title': 'Root Cause Accuracy', 'value': '78.4%', 'comparison': '6.4x vs GPT-4', 'pos': (5, 7)},
        {'title': 'Avg Fix Cycles', 'value': '2.2', 'comparison': '3x faster', 'pos': (8, 7)},
        {'title': 'Retrieval Precision', 'value': '91%', 'comparison': 'with AGR', 'pos': (2, 4)},
        {'title': 'Cost per Success', 'value': '$1.36', 'comparison': '4x cheaper', 'pos': (5, 4)},
        {'title': 'Memory Learning', 'value': '+62%', 'comparison': 'over time', 'pos': (8, 4)}
    ]
    
    for metric in metrics:
        x, y = metric['pos']
        
        # Box
        rect = plt.Rectangle((x-1.3, y-1), 2.6, 1.8, 
                           facecolor='#96CEB4', alpha=0.3, 
                           edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # Title
        ax.text(x, y+0.5, metric['title'], ha='center', va='center', 
                fontsize=12, fontweight='bold')
        
        # Value
        ax.text(x, y, metric['value'], ha='center', va='center', 
                fontsize=20, fontweight='bold', color='#2E7D32')
        
        # Comparison
        ax.text(x, y-0.5, metric['comparison'], ha='center', va='center', 
                fontsize=10, style='italic')
    
    # Add footer
    ax.text(5, 1, 'Available Q4 2025 via Kodezi OS', ha='center', va='center',
            fontsize=14, fontweight='bold', 
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'summary_infographic.png', dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Generate all visualizations."""
    print("Generating visualizations...")
    
    create_overall_performance_comparison()
    print("✓ Overall performance comparison")
    
    create_bug_category_heatmap()
    print("✓ Bug category heatmap")
    
    create_ablation_study_chart()
    print("✓ Ablation study chart")
    
    create_debugging_cycles_distribution()
    print("✓ Debugging cycles distribution")
    
    create_retrieval_performance_chart()
    print("✓ Retrieval performance chart")
    
    create_cost_analysis_chart()
    print("✓ Cost analysis chart")
    
    create_summary_infographic()
    print("✓ Summary infographic")
    
    print(f"\nAll visualizations saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()