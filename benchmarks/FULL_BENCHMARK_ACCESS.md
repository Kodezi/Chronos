# Accessing the Full Chronos Benchmark

## Overview

The complete Kodezi Chronos Multi-Random Retrieval (MRR) benchmark contains 5,000 real-world debugging scenarios, representing the most comprehensive evaluation suite for debugging-focused language models.

## What's Included in This Repository

This repository contains:
- **500 sample test cases** (10% of full benchmark)
- **Evaluation framework** and metrics implementation
- **Sample results** and baseline performance data
- **Documentation** and usage guides

## Full Benchmark Contents

The complete benchmark includes:

### 1. Test Cases (5,000 total)
- 500 syntax error cases
- 1,200 logic bug cases
- 800 concurrency issue cases
- 600 memory-related bug cases
- 900 API misuse cases
- 400 performance bug cases
- 600 cross-category cases

### 2. Repository Snapshots
- 110 real-world repositories with full git history
- Ranging from 1K to 2M+ lines of code
- Multiple programming languages (Python, JavaScript, Java, Go, Rust)
- Each with 20-200 injected bugs

### 3. Temporal Test Data
- Bugs spanning 3-12 months of development history
- Refactoring scenarios with moved/renamed files
- Evolution of codebases over time

### 4. Ground Truth Data
- Expert-validated fixes for all 5,000 bugs
- Multiple valid fix variations where applicable
- Detailed fix explanations and patterns

## Access Requirements

### Academic Researchers
1. **Eligibility**: University-affiliated researchers
2. **Process**:
   - Submit request to research@kodezi.com
   - Include institutional affiliation
   - Describe intended research use
   - Sign data use agreement
3. **Timeline**: 2-3 weeks for approval

### Industry Partners
1. **Eligibility**: Companies developing debugging tools
2. **Process**:
   - Contact partnerships@kodezi.com
   - Provide company information
   - Describe use case and impact
   - Execute partnership agreement
3. **Timeline**: 4-6 weeks for approval

### General Availability
- **Release Date**: Q1 2026
- **Format**: Public research release
- **License**: Apache 2.0 for code, custom license for data

## Data Use Agreement Terms

Users of the full benchmark agree to:
1. Use data only for research/evaluation purposes
2. Not redistribute the raw dataset
3. Cite the Chronos paper in publications
4. Share evaluation results with the community
5. Report any data quality issues found

## How to Request Access

### Email Template
```
To: research@kodezi.com
Subject: Chronos Benchmark Access Request - [Your Institution]

Dear Chronos Team,

I am requesting access to the full Chronos MRR benchmark dataset.

Researcher Information:
- Name: [Your Name]
- Institution: [University/Company]
- Position: [Your Title]
- Email: [Institutional Email]

Research Purpose:
[Describe your intended use of the benchmark]

Expected Outcomes:
[What you plan to publish/release]

I agree to the data use terms and will cite the Chronos paper.

Best regards,
[Your Name]
```

## Working with the Sample Dataset

While waiting for full benchmark access, you can:

1. **Develop your evaluation pipeline** using the 500 sample cases
2. **Test your debugging model** on representative scenarios
3. **Compare against baseline results** provided
4. **Optimize retrieval strategies** for scattered context

The sample dataset is designed to be representative of the full benchmark distribution.

## Citation Requirement

All uses of the Chronos benchmark must cite:

```bibtex
@article{khan2025chronos,
  title={Kodezi Chronos: A Debugging-First Language Model for Repository-Scale, Memory-Driven Code Understanding},
  author={Khan, Ishraq and Chowdary, Assad and Haseeb, Sharoz and Patel, Urvish},
  journal={arXiv preprint arXiv:2507.12482},
  year={2025},
  note={Benchmark available at Q1 2026}
}
```

## Benchmark Versions

- **v1.0-sample** (Current): 500 test cases, available now
- **v1.0-full** (Q1 2026): Complete 5,000 test cases
- **v2.0** (Planned 2026): Extended with additional languages and bug types

## FAQ

### Q: Can I use the sample dataset for commercial evaluation?
A: Yes, the sample dataset is available under Apache 2.0 license.

### Q: Will my model's results be public?
A: You control publication of your results. We encourage sharing for community benefit.

### Q: Can I contribute test cases?
A: Yes! See CONTRIBUTING.md for guidelines on submitting new debugging scenarios.

### Q: Is the evaluation deterministic?
A: Yes, given the same model outputs, evaluation results are reproducible.

### Q: What if my model needs different input format?
A: The evaluation framework is extensible. See the adapter examples in `benchmarks/adapters/`.

## Support

- **Technical Issues**: Open an issue in this repository
- **Access Questions**: research@kodezi.com
- **Partnership Inquiries**: partnerships@kodezi.com

## Updates

Subscribe to our mailing list for updates:
- Benchmark release announcements
- New evaluation metrics
- Community evaluation results
- Workshop and challenge announcements

Sign up at: https://kodezi.com/chronos-updates

---

*The Chronos benchmark represents a significant step forward in debugging model evaluation. We look forward to seeing how the research community uses it to advance the field.*