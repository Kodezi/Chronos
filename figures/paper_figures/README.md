# Paper Figures

This directory contains the 11 figures from the Chronos paper.

## Figures List

1. **fig1_architecture.pdf** - Chronos Architecture Overview
2. **fig2_main_comparison.pdf** - Main Performance Comparison (67.3% vs 13.8%)
3. **fig3_category_performance.pdf** - Performance by Bug Category
4. **fig4_repository_scale.pdf** - Repository Scale Analysis
5. **fig5_debugging_cycles.pdf** - Debugging Cycles Efficiency
6. **fig6_retrieval_depth.pdf** - AGR Retrieval Depth Analysis
7. **fig7_ablation_study.pdf** - Ablation Study Results
8. **fig8_token_efficiency.pdf** - Token Efficiency Comparison
9. **fig9_cost_comparison.pdf** - Cost per Fix Analysis
10. **fig10_language_performance.pdf** - Language-Specific Performance
11. **fig11_learning_curve.pdf** - PDM Learning Curve

## Generation

To generate the actual figures, run:
```bash
pip install matplotlib seaborn pandas numpy
python scripts/generate_all_visualizations.py
```

The figures will be generated in both PNG and PDF formats.