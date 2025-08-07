# Kodezi Chronos 2025 - Figures and Visualizations

This directory contains all figures and visualizations from the Kodezi Chronos 2025 research paper.

## Figure List

### Main Performance Figures

1. **model_comparison.png**
   - Bar chart showing debugging success rates across models
   - Chronos: 67.3%, Claude 4 Opus: 14.2%, GPT-4.1: 13.8%, etc.
   - Shows 4.7x improvement factor

2. **bug_category_performance.png**
   - Dual chart showing:
     - Success rates by bug category for Chronos vs baseline
     - Improvement factors (1.1x to 18.2x)

3. **retrieval_comparison.png**
   - Line graph comparing retrieval strategies
   - Shows AGR achieving 92% precision at 85% recall
   - Compares Flat, BM25, Graph RAG, and Chronos AGR

4. **learning_curve.png**
   - Cross-session learning improvement over time
   - PDM cache hit rate reaching 87%
   - Success rate improvement from 52.1% to 79.2%

5. **limitation_analysis.png**
   - Bar chart of performance on challenging categories
   - Hardware: 23.4%, Dynamic Languages: 41.2%, Distributed: 30%

### Technical Architecture Figures

6. **agr_architecture.png**
   - Adaptive Graph-Guided Retrieval system diagram
   - Shows k-hop expansion and confidence thresholds

7. **seven_layer_architecture.png**
   - Complete Chronos architecture layers
   - From Multi-Source Input to Explainability Layer

8. **debugging_loop_flow.png**
   - Iterative debugging process flowchart
   - Shows 7.8 average iterations to success

### Analysis Figures

9. **flame_graph_example.png**
   - Performance bottleneck visualization
   - CPU usage analysis example

10. **temporal_analysis.png**
    - Bug distribution over time
    - Pattern evolution across project lifecycle

11. **complexity_verification.png**
    - O(k log d) complexity proof
    - Log-log plot with correlation coefficient

12. **summary_dashboard.png**
    - Comprehensive metrics dashboard
    - All key performance indicators in one view

## Generation Instructions

To regenerate these figures with updated data:

```bash
cd benchmarks/comprehensive_benchmarks
python benchmark_visualization.py
```

This will create all figures in the `figures/` directory.

## Figure Specifications

- **Format**: PNG
- **Resolution**: 300 DPI
- **Size**: Optimized for paper publication
- **Color Scheme**: Consistent across all figures
- **Font**: Publication-ready typography

## Usage in Paper

These figures are referenced throughout the research paper:
- Figure 1: Model comparison (Section 3)
- Figure 2: Bug category performance (Section 4.1)
- Figure 3: Retrieval comparison (Section 4.2)
- Figure 4: Learning curve (Section 4.3)
- Figure 5: Limitations (Section 5)

## Data Sources

All figures are generated from:
- MRR benchmark results (5,000 scenarios, 12,500 bugs)
- Real-world evaluation data
- Statistical analysis with 95% confidence intervals
- Cross-validation across multiple runs

## Notes

- Figures use colorblind-friendly palettes
- Error bars included where applicable
- Statistical significance marked
- Consistent styling for paper submission