<div align="center">

# 🚀 Kodezi Chronos

## The World's First Debugging-First Language Model for Repository-Scale, Memory-Driven Code Understanding

[![arXiv](https://img.shields.io/badge/arXiv-2507.12482-b31b1b.svg?style=for-the-badge)](https://arxiv.org/abs/2507.12482)
[![Model Access](https://img.shields.io/badge/Model-Chronos%20Waitlist-4B7BFF.svg?style=for-the-badge)](https://chronos.so)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Research](https://img.shields.io/badge/Research-Paper-orange.svg?style=for-the-badge)](paper/chronos-research.md)
[![Benchmark](https://img.shields.io/badge/Benchmark-MRR-purple.svg?style=for-the-badge)](benchmarks/multi-random-retrieval/)

<img src="https://img.shields.io/badge/Debug%20Success-67.3%25-brightgreen?style=for-the-badge" alt="Debug Success Rate">
<img src="https://img.shields.io/badge/Human%20Preference-89%25-blue?style=for-the-badge" alt="Human Preference">
<img src="https://img.shields.io/badge/Improvement-4--5x-yellow?style=for-the-badge" alt="Improvement over GPT-4.1">
<img src="https://img.shields.io/badge/Time%20Reduction-40%25-orange?style=for-the-badge" alt="Time Reduction">

<h3>🎯 67.3% Autonomous Debugging Success • 🔍 89% Human Preference • ⚡ 7.8 Average Fix Iterations • 💰 40% Time Reduction</h3>

<p align="center">
  <img src="results/figures/architecture_overview.svg" alt="Chronos Architecture" width="800">
</p>

</div>

---

<div align="center">

### ⚠️ Model Access Notice ⚠️

**Chronos is proprietary and available exclusively through Kodezi OS**

| Timeline | Access | Details |
|:--------:|:------:|:-------:|
| **Q4 2025** | Beta | Limited enterprise access |
| **Q1 2026** | GA | Via [Kodezi OS](https://kodezi.com/os) |

This repository contains the MRR benchmark suite and evaluation framework only.

</div>

---

<div align="center">

### 🌟 Revolutionary AI That Debugs Like a Senior Developer

**[Quick Start](QUICK_START.md)** • **[Get Early Access](https://chronos.so)** • **[Read Paper](paper/chronos-research.md)** • **[View Benchmarks](benchmarks/)** • **[Documentation](docs/)** • **[Case Studies](results/case_studies/)**

</div>

---

## 🏆 MRR Benchmark Results

<div align="center">

### Overall Performance (5,000 MRR Scenarios)

| Metric | **Chronos** | **GPT-4.1** | **Claude-4** | **Gemini-2.0** | **Improvement** |
|:------:|:------------------:|:---------:|:-----------------:|:------------------:|:---------------:|
| **Debug Success Rate** | **67.3%** | 13.8% | 14.2% | 15.0% | **4.5x** |
| **Root Cause Accuracy** | **89%*** | 12.3%±1.8% | 11.7%±2.0% | 15.8%±1.5% | **5.6-7.6x** |
| **Average Fix Iterations** | **7.8** | 1-2 | 1-2 | 1-2 | **More thorough** |
| **Retrieval Precision** | **92%*** | 68%±2.3% | 67%±2.4% | 74%±1.8% | **1.2-1.4x** |
| **Time Reduction** | **40%** | - | - | - | **40% faster** |

***p < 0.001 compared to best baseline (two-tailed t-test, n=5,000)**

</div>

### Performance by Bug Category

<div align="center">

| Bug Category | **Chronos** | **GPT-4** | **Claude-3** | **Gemini-1.5** | **Chronos Advantage** |
|:------------:|:-----------:|:---------:|:------------:|:--------------:|:--------------------:|
| **Syntax Errors** | 94.2% | 82.3% | 79.8% | 85.1% | 1.1x |
| **Logic Bugs** | 72.8% | 12.1% | 10.7% | 15.3% | **6.0x** |
| **Concurrency Issues** | 58.3% | 3.2% | 2.8% | 4.1% | **18.2x** |
| **Memory Problems** | 61.7% | 5.7% | 4.3% | 6.9% | **10.8x** |
| **API Misuse** | 79.1% | 18.9% | 16.2% | 22.4% | **4.2x** |
| **Performance Bugs** | 65.4% | 7.4% | 6.1% | 9.8% | **8.8x** |

</div>

### Repository Scale Performance

<div align="center">

| Repository Size | **Chronos Success** | **Best Baseline** | **Baseline Model** | **Improvement** |
|:---------------:|:-------------------:|:-----------------:|:------------------:|:---------------:|
| **<10K LOC** | 71.2%±2.8% | 21.3%±3.5% | Gemini-1.5-Pro | **3.3x** |
| **10K-100K LOC** | 68.9%±2.5% | 14.7%±3.2% | Gemini-1.5-Pro | **4.7x** |
| **100K-1M LOC** | 64.3%±2.9% | 8.9%±2.8% | Gemini-1.5-Pro | **7.2x** |
| **>1M LOC** | 59.7%±3.1% | 3.8%±1.9% | Gemini-1.5-Pro | **15.7x** |

</div>

---

## 🧠 Key Innovations in Chronos

### 1. **Debugging-First Architecture**
- Trained on 42.5M real debugging examples (not code completion)
- Specialized for root cause analysis and multi-file patches
- 78.4% root cause accuracy vs 15.8% best baseline

### 2. **Persistent Debug Memory (PDM)**
- Repository-specific learning from debugging sessions
- Improves from 35% → 65% success rate over time
- Cross-session pattern recognition

### 3. **Adaptive Graph-Guided Retrieval (AGR)**
- O(k log d) complexity with dynamic k-hop expansion
- 92% precision, 85% recall on multi-file context
- Handles unlimited repository scale intelligently

### 4. **Output-Optimized Design**
- Optimized for ~3K output tokens (fixes, tests, docs)
- 47.2% output entropy density vs 12.8% for completion models
- Designed for complex patch generation

### 5. **Autonomous Debugging Loop**
- Average 7.8 iterations to successful fix
- Propose → test → analyze → refine cycles
- 67.3% fully autonomous success rate

---

## 🏗️ Architecture Overview

### Seven-Layer System Design

1. **Multi-Source Input Layer**: Processes code, logs, traces, tests, docs simultaneously
2. **Adaptive Retrieval Engine (AGR)**: Dynamic k-hop graph traversal (92% precision)
3. **Debug-Tuned LLM Core**: 42.5M debugging examples, not code completion
4. **Orchestration Controller**: Autonomous debugging loop management
5. **Persistent Debug Memory**: Repository-specific learning (35% → 65% improvement)
6. **Execution Sandbox**: Isolated test validation environment
7. **Explainability Layer**: Human-readable root cause analysis

See [architecture documentation](architecture/README.md) for detailed specifications.

---

## 📊 Multi-Random Retrieval (MRR) Benchmark

### What is MRR?

MRR simulates real-world debugging complexity by:
- **Spatial Distribution**: Bug context scattered across 10-50 files
- **Temporal Dispersion**: Relevant information from 3-12 months of history
- **Obfuscation Levels**: Low/medium/high code complexity
- **5,000 Scenarios**: Comprehensive evaluation across languages and bug types

### MRR Results

| Metric | Chronos | GPT-4+RAG | Claude-3+VectorDB | Gemini-1.5+Graph |
|:-------|:-------:|:---------:|:-----------------:|:----------------:|
| **Precision@10** | 89.2% | 42.3% | 48.1% | 51.7% |
| **Recall@10** | 84.7% | 31.7% | 36.2% | 41.8% |
| **Fix Accuracy** | 67.3% | 8.9% | 11.2% | 14.6% |
| **Context Efficiency** | 0.71 | 0.23 | 0.28 | 0.31 |

Full benchmark available in [benchmarks/multi-random-retrieval/](benchmarks/multi-random-retrieval/)

---

## 🚀 Getting Started

### Running the MRR Benchmark

```bash
# Clone the repository
git clone https://github.com/kodezi/chronos-research.git
cd chronos-research

# Install dependencies
pip install -r requirements.txt

# Run MRR benchmark on your model
python benchmarks/run_mrr_benchmark_2025.py \
  --model your_model \
  --scenarios 100  # Start with subset

# Analyze results
python benchmarks/analyze_results.py
```

### Model Access

**⚠️ The Chronos model is not included in this repository**

Chronos will be available via [Kodezi OS](https://kodezi.com/os):
- **Q4 2025**: Enterprise beta
- **Q1 2026**: General availability
- **Join waitlist**: [chronos.so](https://chronos.so)

---

## 📁 Repository Contents

```
chronos-research/
├── benchmarks/               # MRR Benchmark Suite
│   ├── multi-random-retrieval/  # 5,000 scenario benchmark
│   ├── evaluation_metrics/      # Metrics implementation
│   └── run_mrr_benchmark_2025.py  # Main benchmark runner
├── reference_implementations/  # Algorithm references (NOT the model)
│   ├── algorithms/            # AGR, PDM implementations
│   └── NOTICE.md             # Proprietary model notice
├── paper/                    # Research paper
│   └── chronos-research-2025.md  # Full paper (arXiv:2507.12482)
├── results/                  # Performance data
│   ├── raw_data/             # 5,000 scenario results
│   └── case_studies/         # Debugging examples
├── figures/                  # Paper visualizations
│   └── paper_figures/        # 11 paper figures
├── docs/                     # Documentation
├── MODEL_ACCESS.md          # How to access Chronos
└── LEADERBOARD.md           # Performance rankings
```

---

## 🔬 Research Highlights

### Training Dataset
- 42.5M debugging examples (not code completion)
- 15M GitHub issues with fixes
- 8M stack traces with resolutions  
- 3M CI/CD debugging logs
- 2.5M production sessions
- 14M curated from Defects4J, SWE-bench, BugsInPy

### AGR Performance
- k=1 hop: 58.2% success
- k=2 hops: 72.4% success
- k=adaptive: 87.1% success
- Flat retrieval: 23.4% success

### PDM Learning Curve
- Initial: 35% success rate
- After 100 sessions: 52% success
- After 500 sessions: 65% success
- 7.3x token efficiency gain

---

## 📈 Detailed Performance Analysis

### Language-Specific Performance

<div align="center">

| Language | **Chronos** | **GPT-4** | **Claude-3** | **Gemini-1.5** | Test Suite |
|:--------:|:-----------:|:---------:|:------------:|:--------------:|:----------:|
| **Python** | 68.7%±2.1% | 11.2%±2.8% | 10.3%±2.9% | 14.6%±2.6% | 1,823 bugs |
| **JavaScript** | 64.2%±2.3% | 7.8%±2.5% | 6.9%±2.6% | 10.1%±2.4% | 1,547 bugs |
| **Java** | 63.9%±2.2% | 6.3%±2.2% | 5.7%±2.3% | 9.2%±2.1% | 1,630 bugs |
| **Go** | 66.8%±2.4% | 9.1%±2.6% | 8.4%±2.7% | 12.3%±2.5% | 892 bugs |
| **C++** | 61.2%±2.6% | 5.2%±2.1% | 4.8%±2.2% | 7.9%±2.0% | 1,108 bugs |

</div>

### Debugging Cycle Efficiency

<div align="center">

| Iteration | **Chronos Success** | **GPT-4 Success** | **Time Reduction** |
|:---------:|:-------------------:|:-----------------:|:------------------:|
| 1st Attempt | 42.3% | 3.2% | -87% time |
| 2nd Attempt | 58.7% (+16.4%) | 5.1% (+1.9%) | -83% time |
| 3rd Attempt | 65.3% (+6.6%) | 6.8% (+1.7%) | -79% time |
| 4+ Attempts | 65.3% (converged) | 8.5% (+1.7%) | -74% time |

</div>

### Context Window Efficiency

<div align="center">

| Model | Context Size | Debug Success | Note |
|:------|:------------:|:-------------:|:-----|
| GPT-4-32K | 32K tokens | 7.2% | More context ≠ better debugging |
| Claude-3-200K | 200K tokens | 9.8% | Attention dilution at scale |
| Gemini-1.5-Pro-1M | 1M tokens | 14.3% | Best traditional model |
| **Chronos** | **Unlimited*** | **71.2%** | *Via intelligent retrieval |

</div>

---

## 🔬 Ablation Studies

<div align="center">

### Component Contribution Analysis

| Configuration | Debug Success | Impact |
|:--------------|:-------------:|:-------|
| **Full Chronos** | **65.3%** | Complete system |
| No Multi-Code Association | 35.8% | -45% performance |
| Static Memory Only | 40.1% | -39% performance |
| No Orchestration Loop | 42.5% | -35% performance |
| No AGR (Flat Retrieval) | 28.7% | -56% performance |

</div>

---

## 📚 Documentation

<div align="center">

| [Getting Started](docs/getting_started.md) | [Architecture](architecture/README.md) | [Benchmarks](benchmarks/README.md) | [API Reference](docs/api_reference.md) |
|:------------------------------------------:|:--------------------------------------:|:----------------------------------:|:--------------------------------------:|
| Quick start guide | System design details | Evaluation methodology | Future API documentation |

| [Performance](performance.md) | [Case Studies](results/case_studies/) | [FAQ](docs/faq.md) | [Limitations](docs/limitations.md) |
|:-----------------------------:|:-------------------------------------:|:------------------:|:----------------------------------:|
| Detailed metrics | Real-world examples | Common questions | Known constraints |

</div>

---

## 🤝 Contributing

We welcome contributions to the evaluation framework and benchmarks!

```bash
# Fork and clone
git clone https://github.com/[your-username]/chronos-research
cd chronos-research

# Create feature branch
git checkout -b feature/your-contribution

# Make changes and test
python -m pytest tests/

# Submit PR
git push origin feature/your-contribution
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📝 Citation

If you use this research in your work, please cite:

```bibtex
@article{khan2025chronos,
  title={Kodezi Chronos: A Debugging-First Language Model for 
         Repository-Scale, Memory-Driven Code Understanding},
  author={Khan, Ishraq and Chowdary, Assad and 
          Haseeb, Sharoz and Patel, Urvish},
  journal={arXiv preprint arXiv:2507.12482},
  year={2025},
  url={https://arxiv.org/abs/2507.12482}
}
```

---

## 🏢 About Kodezi

[Kodezi](https://kodezi.com) is building the future of autonomous software maintenance. Our mission is to empower developers with AI that truly understands code at scale.

---

## 📞 Contact & Community

<div align="center">

### Connect With Us

[![Website](https://img.shields.io/badge/Website-kodezi.com-blue?style=for-the-badge)](https://kodezi.com)
[![Paper](https://img.shields.io/badge/Paper-arXiv:2507.12482-red?style=for-the-badge)](https://arxiv.org/abs/2507.12482)
[![Twitter](https://img.shields.io/badge/Twitter-@KodeziHQ-1DA1F2?style=for-the-badge&logo=twitter)](https://twitter.com/kodezihq)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Kodezi-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/company/kodezi)
[![Email](https://img.shields.io/badge/Email-research@kodezi.com-D14836?style=for-the-badge&logo=gmail)](mailto:research@kodezi.com)

### Join the Discussion

[![GitHub Discussions](https://img.shields.io/badge/GitHub-Discussions-181717?style=for-the-badge&logo=github)](https://github.com/kodezi/chronos/discussions)

</div>

---

## 📄 License

This research repository is licensed under the MIT License - see [LICENSE](LICENSE) for details.

**⚠️ Important**: The Kodezi Chronos model itself is proprietary technology and is not included in this repository. Model waitlist access is available at [chronos.so](https://chronos.so).

---

<div align="center">

### 🚀 The Future of Debugging is Here

<h3>
  
**[Join Waitlist →](https://chronos.so)** | **[Read Paper →](https://arxiv.org/abs/2507.12482)** | **[Learn More →](https://chronos.so)**

</h3>

<sub>Built with ❤️ by the Kodezi Team</sub>

</div>
