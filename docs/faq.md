# Frequently Asked Questions

## General Questions

### Q: What is Kodezi Chronos?
**A:** Kodezi Chronos is the first debugging-first language model specifically designed for autonomous bug detection, root cause analysis, and validated fix generation. It achieves a 65.3% debugging success rate, representing a 6-7x improvement over state-of-the-art models.

### Q: How can I access the Chronos model?
**A:** The Chronos model is proprietary and will be available exclusively through Kodezi OS starting in Q1 2026. Visit [https://kodezi.com/os](https://kodezi.com/os) for access information.

### Q: What makes Chronos different from GitHub Copilot or other code assistants?
**A:** Key differences include:
- **Purpose-built for debugging** (not code completion)
- **Persistent memory** across sessions
- **Autonomous debugging loop** with validation
- **Repository-scale understanding** via AGR
- **Output-optimized architecture** for generating fixes

## Technical Questions

### Q: What is Adaptive Graph-Guided Retrieval (AGR)?
**A:** AGR is Chronos's novel retrieval mechanism that:
- Represents code as a graph with typed relationships
- Dynamically expands retrieval depth based on query complexity
- Achieves unlimited effective context without massive context windows
- Provides 5x better debugging success than flat retrieval

### Q: How does Chronos handle large repositories (>1M LOC)?
**A:** Chronos maintains strong performance on large codebases through:
- Hierarchical embeddings (token → statement → function → module)
- Lazy loading with smart caching
- AGR's focused retrieval (only relevant context)
- Success rate of 59.7% even on 1M+ LOC repos

### Q: What programming languages does Chronos support?
**A:** The research focused on Python, JavaScript, and Java. Additional language support will be announced closer to the release date.

### Q: Can Chronos fix all types of bugs?
**A:** No. Chronos excels at:
- Logic errors (72.8% success)
- API issues (79.1% success)
- Concurrency bugs (58.3% success)

But struggles with:
- Hardware-specific bugs (23.4% success)
- Domain-specific logic requiring deep expertise (28.7% success)
- UI/visual bugs (8.3% success)

## Research Questions

### Q: How was the 65.3% success rate measured?
**A:** Success rate was measured on 5,000 real-world debugging scenarios where:
- Each bug had a verified human fix
- Success meant the generated fix passed all tests
- No regressions were introduced
- Results were statistically validated (p < 0.001)

### Q: What is the Multi Random Retrieval (MRR) benchmark?
**A:** MRR is our novel benchmark that:
- Scatters debugging context across 10-50 files
- Includes temporal dispersion (3-12 months)
- Features obfuscated dependencies
- Better reflects real-world debugging complexity

### Q: Can I reproduce the evaluation results?
**A:** While the model is proprietary, you can:
- Use our benchmark specifications
- Apply our evaluation protocols to your models
- Compare results using our metrics
- Access anonymized result data

## Practical Questions

### Q: When will Chronos be available?
**A:** 
- **Q1 2026**: Full release via Kodezi OS platform
- **Early Access**: Join the waitlist at [kodezi.com/os](https://kodezi.com/os)

### Q: How much will Chronos cost?
**A:** Pricing will be announced closer to release. The research shows an effective cost of $1.36 per successfully fixed bug, compared to $5.53-$6.67 for competing models.

### Q: Can Chronos be integrated with my existing tools?
**A:** Yes, Chronos will integrate with:
- Popular IDEs (VS Code, IntelliJ, etc.)
- CI/CD pipelines
- Code review systems
- Issue tracking platforms

### Q: Does Chronos require internet connectivity?
**A:** Details about deployment options (cloud vs. on-premise) will be announced with the product release.

## Privacy and Security

### Q: How does Chronos handle proprietary code?
**A:** 
- Persistent memory is stored locally per repository
- No code sharing between organizations
- Enterprise deployment options available
- SOC 2 compliance planned

### Q: Can Chronos introduce security vulnerabilities?
**A:** Chronos includes:
- Automated security scanning of generated fixes
- Sandboxed execution environment
- Regression testing to prevent new vulnerabilities
- Option to require human approval for sensitive code

## Research Collaboration

### Q: Can I contribute to Chronos research?
**A:** Yes! You can:
- Submit benchmark improvements
- Propose new evaluation metrics
- Share anonymized debugging scenarios
- Contribute to analysis tools

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

### Q: How do I cite the Chronos research?
**A:** Use the BibTeX citation:
```bibtex
@article{khan2025chronos,
  title={Kodezi Chronos: A Debugging-First Language Model for Repository-Scale, Memory-Driven Code Understanding},
  author={Khan, Ishraq and Chowdary, Assad and Haseeb, Sharoz and Patel, Urvish},
  journal={arXiv preprint arXiv:2507.12482},
  year={2025}
}
```

## Contact

### Q: Who do I contact for:

- **Research questions**: research@kodezi.com
- **Model access**: sales@kodezi.com  
- **Partnership opportunities**: partners@kodezi.com
- **Technical support**: support@kodezi.com
- **Media inquiries**: press@kodezi.com

### Q: Where can I learn more?
- Research paper: [arXiv:2507.12482](https://arxiv.org/abs/2507.12482)
- Kodezi website: [https://kodezi.com](https://kodezi.com)
- GitHub: [https://github.com/kodezi/chronos-research](https://github.com/kodezi/chronos-research)