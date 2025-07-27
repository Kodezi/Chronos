# Kodezi Chronos Figures

This directory contains conceptual diagrams and visualizations from the Kodezi Chronos research paper.

## ⚠️ Important Notice

The Kodezi Chronos model is **proprietary** and available exclusively through [Kodezi OS](https://kodezi.com/os) starting Q1 2026.

## 📊 Figure List

### 1. architecture_overview.svg
High-level overview of Chronos's 7-layer architecture showing the flow from multi-source input through memory engine, retrieval, and reasoning to validated outputs.

### 2. token_flow_diagram.svg
Visualization of debugging token distribution showing the output-heavy nature of debugging (input ~3.6K tokens vs output ~3K tokens).

### 3. memory_graph.svg
Graph-structured memory indexing showing how code, documentation, and test elements are connected as nodes with functional relationships as edges.

### 4. feedback_loop.svg
The autonomous debugging feedback loop illustrating the iterative process of generation, validation, refinement, and memory update.

### 5. debug_loop.svg
Simplified debugging loop showing the core cycle: Detect → Retrieve → Propose → Test → Decide.

### 6. retrieval_mechanism.svg
Multi-modal retrieval mechanism showing how queries flow through vector, AST, graph, and history indices.

### 7. traditional_vs_agr.svg
Comparison between traditional LLM planning (23% success) and AGR-enhanced debugging (87% success).

### 8. iterative_expansion.svg
Visualization of iterative context expansion in AGR, showing k-hop neighbor retrieval.

### 9. debug_cycles_chart.svg
Bar chart comparing average debug cycles: Chronos (2.2) vs baselines (5.1-6.8).

### 10. ablation_analysis.svg
Component importance analysis showing performance drops when removing key features.

## 🎨 Figure Generation

These figures are conceptual representations based on the research paper. They illustrate:
- System architecture and data flow
- Performance comparisons
- Algorithmic concepts
- Evaluation results

## 📈 Key Visual Insights

1. **Architecture Complexity**: The 7-layer architecture demonstrates the sophisticated design required for effective debugging
2. **Output-Heavy Nature**: Unlike typical LLMs, debugging requires substantial output generation
3. **Graph-Based Memory**: Shows why traditional flat retrieval fails for debugging tasks
4. **Iterative Refinement**: Illustrates why single-shot generation doesn't work for debugging

## 🔍 Usage

These figures are provided for:
- Understanding Chronos's architecture
- Academic presentations
- Research comparisons
- Documentation purposes

## 📚 Citation

When using these figures, please cite:

```bibtex
@article{khan2025chronos,
  title={Kodezi Chronos: A Debugging-First Language Model for 
         Repository-Scale, Memory-Driven Code Understanding},
  author={Khan, Ishraq and Chowdary, Assad and 
          Haseeb, Sharoz and Patel, Urvish},
  journal={arXiv preprint arXiv:2507.12482},
  year={2025}
}
```

---

**Note**: Actual model implementation and weights are proprietary to Kodezi Inc.