#!/usr/bin/env python3
"""
Generate visualizations for Kodezi Chronos 2025 paper figures
"""

import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

# Set style for academic papers
plt.style.use('seaborn-v0_8-paper')
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['legend.fontsize'] = 12

def create_token_distribution_fig1():
    """Fig. 1: Token distribution in debugging tasks"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Input tokens
    input_categories = ['Stack Trace', 'Code Context', 'Logs/Tests', 'Fix History']
    input_tokens = [300, 2000, 800, 500]
    
    ax1.bar(input_categories, input_tokens, color='#3498db')
    ax1.set_title('Input (Sparse)')
    ax1.set_ylabel('Tokens')
    ax1.set_ylim(0, 2500)
    
    # Output tokens  
    output_categories = ['Bug Fix', 'Explanation', 'Tests', 'Docs/PR', 'Fallback']
    output_tokens = [1200, 500, 600, 400, 300]
    
    ax2.bar(output_categories, output_tokens, color='#e74c3c')
    ax2.set_title('Output (Dense)')
    ax2.set_ylabel('Tokens')
    ax2.set_ylim(0, 2500)
    
    plt.tight_layout()
    plt.savefig('figures/fig1_token_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_capability_comparison_fig2():
    """Fig. 2: Debugging capability comparison"""
    categories = ['Context\\nRetrieval', 'Memory\\nUsage', 'Test\\nIntegration', 
                  'Multi-File\\nSupport', 'Error\\nAnalysis', 'Fix\\nGeneration',
                  'Iteration\\nSpeed', 'Cost\\nEfficiency']
    
    chronos_scores = [95, 98, 92, 96, 88, 91, 95, 91]
    claude4_scores = [68, 20, 45, 55, 62, 58, 30, 45]
    gpt41_scores = [70, 22, 48, 58, 60, 55, 32, 48]
    
    x = np.arange(len(categories))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.bar(x - width, chronos_scores, width, label='Chronos', color='#2ecc71')
    ax.bar(x, claude4_scores, width, label='Claude 4 Opus', color='#9b59b6')
    ax.bar(x + width, gpt41_scores, width, label='GPT-4.1', color='#f39c12')
    
    ax.set_ylabel('Performance (%)')
    ax.set_title('Debugging Capability Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 110)
    
    plt.tight_layout()
    plt.savefig('figures/fig2_capability_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_fix_loop_lifecycle_fig3():
    """Fig. 3: Complete fix loop lifecycle"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # This would be a complex flow diagram - simplified representation
    stages = ['Bug Triggered', 'PDM Access', 'AGR Retrieval', 'Plan Generation',
              'Context Assembly', 'Patch Drafted', 'Test Executed', 'Pass/Fail?']
    
    y_positions = np.linspace(1, 0, len(stages))
    
    for i, (stage, y) in enumerate(zip(stages, y_positions)):
        ax.text(0.5, y, stage, ha='center', va='center', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
        
        if i < len(stages) - 1:
            ax.arrow(0.5, y - 0.05, 0, -0.08, head_width=0.03, head_length=0.02,
                    fc='black', ec='black')
    
    # Add feedback loop
    ax.annotate('', xy=(0.7, 0.85), xytext=(0.7, 0.15),
                arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=0.3",
                              linestyle='--', color='red'))
    ax.text(0.8, 0.5, 'Refine\\n+ Retry\\n(Avg 7.8)', ha='center', color='red')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.1, 1.1)
    ax.axis('off')
    ax.set_title('Complete Fix Loop Lifecycle', fontsize=16, pad=20)
    
    plt.savefig('figures/fig3_fix_loop_lifecycle.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_comparison_fig21():
    """Fig. 21: Comprehensive performance comparison"""
    metrics = ['Debug\\nSuccess', 'Precision', 'Recall', 'Human\\nPreference',
               'Time\\nReduction', 'Cost\\nEfficiency']
    
    chronos = [67.3, 92, 85, 89, 40, 85]
    claude4 = [14.2, 67, 62, 0, 0, 20]
    gpt41 = [13.8, 68, 63, 0, 0, 22]
    
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    chronos += chronos[:1]
    claude4 += claude4[:1]
    gpt41 += gpt41[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    ax.plot(angles, chronos, 'o-', linewidth=2, label='Chronos 2.0', color='#2ecc71')
    ax.fill(angles, chronos, alpha=0.25, color='#2ecc71')
    
    ax.plot(angles, claude4, 'o-', linewidth=2, label='Claude 4 Opus', color='#9b59b6')
    ax.fill(angles, claude4, alpha=0.25, color='#9b59b6')
    
    ax.plot(angles, gpt41, 'o-', linewidth=2, label='GPT-4.1', color='#f39c12')
    ax.fill(angles, gpt41, alpha=0.25, color='#f39c12')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 100)
    ax.set_title('Comprehensive Performance Comparison', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    plt.tight_layout()
    plt.savefig('figures/fig21_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_ablation_analysis_fig18():
    """Fig. 18: Ablation analysis"""
    configurations = ['Base\\nModel', '+ Debug\\nTraining', '+ Execution\\nSandbox',
                      '+ Persistent\\nMemory', '+ AGR\\n(Full)']
    success_rates = [8.3, 24.7, 41.2, 55.8, 67.3]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(configurations, success_rates, color=['#e74c3c', '#f39c12', 
                                                        '#3498db', '#9b59b6', '#2ecc71'])
    
    # Add value labels
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate}%', ha='center', va='bottom')
    
    ax.set_ylabel('Debug Success Rate (%)')
    ax.set_title('Ablation Analysis: Impact of Each Component')
    ax.set_ylim(0, 80)
    
    # Add improvement annotations
    for i in range(1, len(success_rates)):
        improvement = success_rates[i] - success_rates[i-1]
        ax.annotate(f'+{improvement:.1f}%', 
                    xy=(i-0.5, (success_rates[i] + success_rates[i-1])/2),
                    ha='center', fontsize=10, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig('figures/fig18_ablation_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Create figures directory
    Path('figures').mkdir(exist_ok=True)
    
    print("Generating 2025 paper figures...")
    
    # Generate all figures
    create_token_distribution_fig1()
    print("✓ Figure 1: Token distribution")
    
    create_capability_comparison_fig2()
    print("✓ Figure 2: Capability comparison")
    
    create_fix_loop_lifecycle_fig3()
    print("✓ Figure 3: Fix loop lifecycle")
    
    create_ablation_analysis_fig18()
    print("✓ Figure 18: Ablation analysis")
    
    create_performance_comparison_fig21()
    print("✓ Figure 21: Performance comparison")
    
    print("\\nAll figures generated successfully!")

if __name__ == "__main__":
    main()