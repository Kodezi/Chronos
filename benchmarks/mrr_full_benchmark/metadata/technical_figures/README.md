# Technical Figures Directory

This directory contains visual representations of the Chronos architecture and performance metrics.

## Figure List

### Architecture Diagrams
- **debugging_paradigm.svg**: Comparison between code completion and debugging approaches
- **agr_graph_structure.svg**: Adaptive Graph-Guided Retrieval architecture
- **memory_graph_nodes.svg**: Node types and relationships in the memory graph
- **chain_of_cause.svg**: Chain-of-cause reasoning vs next-token prediction

### Performance Charts
- **token_distribution.svg**: Input vs output token distribution in debugging
- **accuracy_vs_context.svg**: Debugging accuracy vs context window size
- **time_to_fix.svg**: Time to first valid fix by repository size
- **cost_efficiency.svg**: Cost per successful fix comparison

### Data Flow Diagrams
- **retrieval_flow.svg**: AGR retrieval algorithm flow
- **attention_mechanism.svg**: Dynamic attention scoring system
- **multi_modal_integration.svg**: How different artifact types are integrated

### Benchmark Results
- **mrr_scores.svg**: MRR benchmark performance comparison
- **bug_category_success.svg**: Success rates by bug category
- **scalability_metrics.svg**: Performance at different scales

## Figure Format

All figures are provided in SVG format for scalability and can be converted to other formats as needed. The figures use a consistent color scheme:

- **Chronos/AGR**: Blue (#2E86AB)
- **Traditional LLMs**: Gray (#6C757D)
- **Success/Positive**: Green (#28A745)
- **Error/Negative**: Red (#DC3545)
- **Warning/Caution**: Yellow (#FFC107)

## Usage

These figures can be embedded in documentation, presentations, or papers using standard markdown or HTML:

```markdown
![AGR Architecture](technical_figures/agr_graph_structure.svg)
```

## Generation

Figures are generated from the data in PERFORMANCE_METRICS.md and the architectural descriptions in other technical documents. To regenerate figures with updated data, use the scripts in the `scripts/` directory.