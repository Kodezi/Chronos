# Changelog

All notable changes to the Kodezi Chronos research repository will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-07-29

### Added
- New co-author: Yousuf Zaii
- Updated 2025 research paper with latest findings
- Enhanced benchmark results (12,500 total bugs evaluated)
- New model comparisons (Claude Opus 4, GPT-4.1, DeepSeek V3, Gemini 2.0 Pro)
- Human preference evaluation (N=50, 89% preference)
- Cohen's d effect size analysis (d=3.87)
- O(k log d) complexity proof for AGR
- Hardware-dependent and dynamic language limitation analysis
- 2025 evaluation framework (evaluate_2025.py)
- Visualization generation scripts for paper figures
- Comprehensive 2025 architecture documentation

### Changed
- Debug success rate: 65.3% → 67.3% (±2.1%)
- Retrieval precision: 91% → 92%
- Average iterations: 2.2 → 7.8 (more thorough debugging)
- Comparison baseline: GPT-4 → GPT-4.1 and Claude-4-Opus
- Performance improvement: 6-7x → 4-5x (against stronger baselines)

### Updated
- README.md with 2025 performance metrics
- CITATION.cff with new author and version 2.0.0
- Architecture documentation with 4-pillar design
- Benchmark documentation with expanded test suite
- Performance tables with latest model comparisons

## [1.0.0] - 2025-07-14

### Added
- Initial release of Kodezi Chronos research repository
- Complete research paper (arXiv:2507.12482)
- Multi Random Retrieval (MRR) benchmark specification
- Comprehensive evaluation results and metrics
- Adaptive Graph-Guided Retrieval (AGR) documentation
- Architecture overview and design principles
- Case studies demonstrating debugging capabilities
- Contribution guidelines and code of conduct
- FAQ and documentation

### Research Highlights
- 65.3% debugging success rate (6-7x improvement over GPT-4)
- 78.4% root cause accuracy
- 91% retrieval precision with AGR
- 40% reduction in debugging cycles
- Successful handling of repository-scale contexts

### Benchmark Results
- 5,000 real-world debugging scenarios evaluated
- Statistical significance (p < 0.001) across all metrics
- Comprehensive ablation studies
- Performance analysis across bug categories and repo sizes

### Documentation
- Complete API design documentation
- Evaluation methodology and protocols
- Reproduction guidelines for researchers
- Integration patterns for future deployment

### Known Limitations
- Lower performance on hardware-specific bugs (23.4%)
- Challenges with domain-specific logic (28.7%)
- Limited effectiveness on UI/visual bugs (8.3%)

## Future Releases

### [Planned for Q4 2025]
- Model release through Kodezi OS platform
- Additional language support announcements
- Extended benchmark suite
- Performance optimizations

### [Planned for Q1 2026]
- Full Kodezi OS integration
- Enterprise deployment options
- Advanced debugging features
- Cross-repository capabilities

---

For more information about Kodezi Chronos:
- Research Paper: [arXiv:2507.12482](https://arxiv.org/abs/2507.12482)
- Model Access: [https://kodezi.com/os](https://kodezi.com/os)
- Contact: research@kodezi.com