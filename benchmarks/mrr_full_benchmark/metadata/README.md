# Metadata Directory

This directory contains configuration files, statistics, and technical specifications for the MRR benchmark.

## Files

### benchmark_architecture.yaml
Complete technical specification of the MRR benchmark including:
- Training data requirements (42.5M examples)
- Performance targets and baselines
- Bug category definitions
- Evaluation metrics
- Resource requirements

### category_statistics.json
Detailed statistics for each bug category:
- Bug counts and subcategory distribution
- Language distribution
- Complexity metrics
- Average scattered files and temporal spans

### evaluation_config.yaml
Configuration for running benchmark evaluations:
- Runtime parameters and limits
- Evaluation modes (full, quick, category-specific)
- Metrics configuration
- Output and reporting settings
- Validation rules

### technical_figures/
Directory containing visual representations:
- Architecture diagrams
- Performance charts
- Data flow diagrams
- Benchmark comparison graphs

## Usage

These metadata files are used by:
1. The evaluation framework to configure benchmark runs
2. Analysis scripts to generate reports
3. Researchers to understand benchmark design
4. Model developers to target performance goals

## Key Statistics

- **Total Bugs**: 5,000
- **Bug Categories**: 7
- **Total Artifacts**: 220,871
- **Languages**: JavaScript, Python, Java
- **Average Scattered Files**: 22.4
- **Average Temporal Span**: 182.7 days

## Performance Targets

Based on Chronos architecture:
- Root Cause Accuracy: 78.4%
- Fix Success Rate: 65.3%
- Multi-File Support: Excellent
- Context Efficiency: 87.6%