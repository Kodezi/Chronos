#!/usr/bin/env python3
"""
Generate publication-ready figures for Kodezi Chronos 2025 paper
Creates all figures referenced in the research paper
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from typing import List, Dict, Any
import json

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def create_architecture_diagram():
    """Create the 7-layer architecture diagram"""
    fig, ax = plt.subplots(figsize=(10, 12))
    
    layers = [
        ("7. Explainability Layer", "#E74C3C", "Human-readable explanations"),
        ("6. Execution Sandbox", "#3498DB", "Safe test execution"),
        ("5. Persistent Debug Memory", "#9B59B6", "15M+ sessions, 87% cache hit"),
        ("4. Orchestration Controller", "#1ABC9C", "7.8 avg iterations"),
        ("3. Debug-Tuned LLM Core", "#F39C12", "Specialized transformer"),
        ("2. Adaptive Retrieval Engine", "#2ECC71", "AGR: 92% precision @ 85% recall"),
        ("1. Multi-Source Input Layer", "#34495E", "Heterogeneous signals")
    ]
    
    y_positions = np.linspace(0.1, 0.9, len(layers))
    layer_height = 0.12
    
    for i, (layer_name, color, description) in enumerate(layers):
        # Draw layer box
        rect = mpatches.FancyBboxPatch(
            (0.1, y_positions[i] - layer_height/2), 0.8, layer_height,
            boxstyle="round,pad=0.02",
            facecolor=color,
            edgecolor='black',
            alpha=0.8,
            linewidth=2
        )
        ax.add_patch(rect)
        
        # Add layer text
        ax.text(0.5, y_positions[i], layer_name,
                ha='center', va='center',
                fontsize=14, fontweight='bold',
                color='white')
        
        # Add description
        ax.text(0.92, y_positions[i], description,
                ha='left', va='center',
                fontsize=10, style='italic')
        
        # Add arrows between layers
        if i < len(layers) - 1:
            ax.arrow(0.5, y_positions[i] + layer_height/2 + 0.01,
                    0, y_positions[i+1] - y_positions[i] - layer_height - 0.02,
                    head_width=0.03, head_length=0.01,
                    fc='black', ec='black', alpha=0.5)
    
    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Kodezi Chronos 7-Layer Architecture', fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('seven_layer_architecture.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_agr_flow_diagram():
    """Create AGR algorithm flow diagram"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define flow components
    components = [
        {"pos": (0.2, 0.8), "text": "Debug Query", "color": "#E74C3C"},
        {"pos": (0.2, 0.6), "text": "Extract Seeds\n(Top-5)", "color": "#3498DB"},
        {"pos": (0.5, 0.8), "text": "Estimate k\n(Complexity)", "color": "#9B59B6"},
        {"pos": (0.5, 0.6), "text": "k-hop Expansion", "color": "#2ECC71"},
        {"pos": (0.5, 0.4), "text": "Calculate\nConfidence", "color": "#F39C12"},
        {"pos": (0.8, 0.6), "text": "Check\nTermination", "color": "#1ABC9C"},
        {"pos": (0.8, 0.2), "text": "Return Context\n(92% precision)", "color": "#27AE60"}
    ]
    
    # Draw components
    for comp in components:
        circle = plt.Circle(comp["pos"], 0.08, color=comp["color"], alpha=0.8)
        ax.add_patch(circle)
        ax.text(comp["pos"][0], comp["pos"][1], comp["text"],
                ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Draw arrows
    arrows = [
        ((0.2, 0.72), (0.2, 0.68)),  # Query to Seeds
        ((0.28, 0.6), (0.42, 0.6)),   # Seeds to k-hop
        ((0.2, 0.72), (0.42, 0.78)),  # Query to Estimate k
        ((0.5, 0.72), (0.5, 0.68)),   # k to expansion
        ((0.5, 0.52), (0.5, 0.48)),   # Expansion to confidence
        ((0.58, 0.6), (0.72, 0.6)),   # Expansion to termination
        ((0.5, 0.32), (0.42, 0.52)),  # Confidence loop back
        ((0.8, 0.52), (0.8, 0.28))    # Termination to return
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black', alpha=0.6))
    
    # Add annotations
    ax.text(0.35, 0.3, "< threshold", fontsize=10, style='italic', color='red')
    ax.text(0.9, 0.4, ">= 92%\nthreshold", fontsize=10, style='italic', color='green')
    
    # Add complexity annotation
    ax.text(0.5, 0.05, "O(k log d) Complexity Guaranteed", 
            ha='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.5))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Adaptive Graph-Guided Retrieval (AGR) Flow', fontsize=18, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('agr_flow_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_debugging_loop():
    """Create iterative debugging loop diagram"""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Define loop stages
    stages = [
        {"angle": 0, "label": "Detect\nIssue", "color": "#E74C3C"},
        {"angle": 60, "label": "Retrieve\nContext", "color": "#3498DB"},
        {"angle": 120, "label": "Propose\nFix", "color": "#9B59B6"},
        {"angle": 180, "label": "Run\nTests", "color": "#F39C12"},
        {"angle": 240, "label": "Validate\nSuccess", "color": "#1ABC9C"},
        {"angle": 300, "label": "Update\nMemory", "color": "#2ECC71"}
    ]
    
    # Draw circular flow
    radius = 0.3
    center = (0.5, 0.5)
    
    for stage in stages:
        angle_rad = np.radians(stage["angle"])
        x = center[0] + radius * np.cos(angle_rad)
        y = center[1] + radius * np.sin(angle_rad)
        
        # Draw stage circle
        circle = plt.Circle((x, y), 0.08, color=stage["color"], alpha=0.8)
        ax.add_patch(circle)
        
        # Add label
        label_x = center[0] + (radius + 0.15) * np.cos(angle_rad)
        label_y = center[1] + (radius + 0.15) * np.sin(angle_rad)
        ax.text(label_x, label_y, stage["label"],
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Draw arrow to next stage
        next_angle = np.radians((stage["angle"] + 60) % 360)
        arrow_start_x = x + 0.06 * np.cos(angle_rad + np.pi/3)
        arrow_start_y = y + 0.06 * np.sin(angle_rad + np.pi/3)
        arrow_end_x = center[0] + radius * np.cos(next_angle) - 0.06 * np.cos(next_angle - np.pi/3)
        arrow_end_y = center[1] + radius * np.sin(next_angle) - 0.06 * np.sin(next_angle - np.pi/3)
        
        ax.annotate('', xy=(arrow_end_x, arrow_end_y), 
                   xytext=(arrow_start_x, arrow_start_y),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black', alpha=0.6))
    
    # Add center annotation
    ax.text(center[0], center[1], "7.8\nAverage\nIterations", 
            ha='center', va='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
    
    # Add success rate annotation
    ax.text(0.5, 0.05, "67.3% Debug Success Rate", 
            ha='center', fontsize=16, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.8))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Chronos Iterative Debugging Loop', fontsize=18, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('debugging_loop_flow.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_memory_architecture():
    """Create PDM (Persistent Debug Memory) architecture diagram"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Memory layers
    layers = [
        {"y": 0.7, "width": 0.8, "label": "Global Patterns\n(Cross-repository)", "color": "#E74C3C"},
        {"y": 0.5, "width": 0.6, "label": "Repository Memory\n(Project-specific)", "color": "#3498DB"},
        {"y": 0.3, "width": 0.4, "label": "Session Cache\n(Current debug)", "color": "#2ECC71"}
    ]
    
    for layer in layers:
        rect = mpatches.FancyBboxPatch(
            ((1-layer["width"])/2, layer["y"]-0.08), layer["width"], 0.16,
            boxstyle="round,pad=0.02",
            facecolor=layer["color"],
            alpha=0.7,
            edgecolor='black',
            linewidth=2
        )
        ax.add_patch(rect)
        ax.text(0.5, layer["y"], layer["label"],
                ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Add statistics
    stats = [
        {"pos": (0.85, 0.7), "text": "15M+\nSessions"},
        {"pos": (0.85, 0.5), "text": "87%\nCache Hit"},
        {"pos": (0.85, 0.3), "text": "47ms\nRetrieval"}
    ]
    
    for stat in stats:
        ax.text(stat["pos"][0], stat["pos"][1], stat["text"],
                ha='center', va='center', fontsize=11,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.6))
    
    # Add data flow arrows
    ax.arrow(0.15, 0.15, 0, 0.45, head_width=0.02, head_length=0.02,
             fc='green', ec='green', alpha=0.5)
    ax.text(0.12, 0.1, "Learn", fontsize=10, style='italic')
    
    ax.arrow(0.85, 0.85, 0, -0.45, head_width=0.02, head_length=0.02,
             fc='blue', ec='blue', alpha=0.5)
    ax.text(0.88, 0.9, "Retrieve", fontsize=10, style='italic')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Persistent Debug Memory (PDM) Architecture', fontsize=18, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('pdm_architecture.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def main():
    """Generate all paper figures"""
    print("Generating Kodezi Chronos 2025 Paper Figures...")
    print("=" * 50)
    
    # Architecture diagrams
    print("Creating architecture diagrams...")
    create_architecture_diagram()
    create_agr_flow_diagram()
    create_debugging_loop()
    create_memory_architecture()
    
    # Performance figures are created by benchmark_visualization.py
    print("\nArchitecture diagrams created!")
    print("For performance figures, run: python benchmark_visualization.py")
    
    print("\nAll figures saved to current directory.")

if __name__ == "__main__":
    main()