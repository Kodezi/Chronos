# Kodezi Chronos Figures and Diagrams

This directory contains all figures, diagrams, and visualizations from the Kodezi Chronos research paper. High-resolution versions are available for publication and presentation use.

## Figure List

### 1. System Architecture (architecture.svg)
**Description**: High-level overview of the Chronos 7-layer architecture
- Shows all major components and data flow
- Highlights the debugging-first design
- Illustrates memory and retrieval systems
- **Dimensions**: 1920x1080
- **Format**: SVG (scalable)

### 2. Debugging Loop (debugging-loop.svg)
**Description**: The autonomous debugging loop workflow
- Shows iterative refinement process
- Illustrates test validation cycle
- Demonstrates memory update mechanism
- **Dimensions**: 1600x900
- **Format**: SVG (scalable)

### 3. AGR Mechanism (agr-mechanism.svg)
**Description**: Adaptive Graph-Guided Retrieval visualization
- k-hop expansion illustration
- Confidence-based termination
- Graph traversal examples
- **Dimensions**: 1800x1200
- **Format**: SVG (scalable)

### 4. Performance Comparison (performance-comparison.png)
**Description**: Bar chart comparing debugging success rates
- Shows all baseline models
- Highlights 6-7x improvement
- Includes confidence intervals
- **Dimensions**: 1200x800
- **Resolution**: 300 DPI

### 5. Bug Category Heatmap (bug-category-heatmap.png)
**Description**: Performance across different bug types
- 6 bug categories × 4 models
- Color-coded success rates
- Shows Chronos superiority
- **Dimensions**: 1400x800
- **Resolution**: 300 DPI

### 6. Ablation Study Impact (ablation-impact.png)
**Description**: Component contribution analysis
- Shows performance drop when components removed
- Validates architectural decisions
- Includes statistical significance
- **Dimensions**: 1200x800
- **Resolution**: 300 DPI

### 7. Cost Effectiveness (cost-effectiveness.png)
**Description**: ROI and cost analysis
- Cost per successful debug
- Comparison with human debugging
- Annual savings projection
- **Dimensions**: 1200x600
- **Resolution**: 300 DPI

### 8. Debugging Cycles Distribution (debugging-cycles.png)
**Description**: Histogram of iterations needed
- Shows Chronos converges faster
- Cumulative success overlay
- Comparison with GPT-4
- **Dimensions**: 1400x600
- **Resolution**: 300 DPI

### 9. Retrieval Performance (retrieval-performance.png)
**Description**: AGR vs traditional retrieval
- Precision/Recall curves
- k-hop analysis
- Context efficiency metrics
- **Dimensions**: 1200x800
- **Resolution**: 300 DPI

### 10. Token Distribution (token-distribution.png)
**Description**: Input vs Output token analysis
- Shows debugging is output-heavy
- Justifies architectural choices
- Comparison across tasks
- **Dimensions**: 1000x600
- **Resolution**: 300 DPI

## Placeholder Notes

**Note**: These are placeholder descriptions. The actual figures would be generated using the visualization scripts and data from the evaluation results. To generate the actual figures:

```bash
cd scripts
python generate_visualizations.py
```

## Usage Guidelines

1. **For Papers**: Use SVG versions when possible for scalability
2. **For Presentations**: PNG versions are optimized for projection
3. **For Web**: Consider using compressed versions (add `-web` suffix)
4. **Attribution**: Please cite the paper when using these figures

## Color Scheme

- **Chronos**: #96CEB4 (mint green)
- **GPT-4**: #FF6B6B (coral red)
- **Claude-3**: #4ECDC4 (turquoise)
- **Gemini-1.5**: #45B7D1 (sky blue)
- **Background**: #F7F9FB (light gray)
- **Text**: #2D3436 (dark gray)

## Accessibility

All figures include:
- High contrast colors
- Clear labels and legends
- Alternative text descriptions
- Pattern options for colorblind users

## Generating Figures

To regenerate figures from raw data:

```python
# Example for performance comparison
import matplotlib.pyplot as plt
import pandas as pd

# Load data
df = pd.read_csv('../results/performance_tables/overall_comparison.csv')

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))
# ... plotting code ...
plt.savefig('performance-comparison.png', dpi=300, bbox_inches='tight')
```

## License

These figures are part of the Kodezi Chronos research and are licensed under MIT License. Please cite the paper when using these visualizations.