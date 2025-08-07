# Chronos MRR Benchmark Leaderboard

## Overall Performance (5,000 scenarios)

| Model | Success Rate | Precision | Recall | Avg Iterations | Cost/Fix |
|-------|--------------|-----------|--------|----------------|----------|
| **Chronos*** | 67.3%±2.1% | 92% | 85% | 7.8 | $1.36 |
| Gemini-2.0 Pro | 15.0%±1.5% | 74% | 38% | 19.2 | $4.25 |
| Claude-4 Opus | 14.2%±1.3% | 67% | 34% | 21.8 | $4.89 |
| GPT-4.1 | 13.8%±1.2% | 68% | 32% | 23.5 | $5.53 |
| DeepSeek-V2 | 8.7%±0.9% | 52% | 21% | 28.1 | $7.82 |
| Mistral-Large | 9.2%±0.8% | 48% | 19% | 31.7 | $8.95 |

*Chronos model available via Kodezi OS only

## Category Performance

### Syntax Errors (500 scenarios)
| Model | Success Rate | Improvement vs GPT-4 |
|-------|--------------|---------------------|
| Chronos | 94.2% | 1.1x |
| GPT-4.1 | 82.3% | - |
| Claude-4 | 79.8% | 0.97x |
| Gemini-2.0 | 85.1% | 1.03x |

### Logic Errors (1,200 scenarios)
| Model | Success Rate | Improvement vs GPT-4 |
|-------|--------------|---------------------|
| Chronos | 72.8% | 6.0x |
| GPT-4.1 | 12.1% | - |
| Claude-4 | 10.7% | 0.88x |
| Gemini-2.0 | 15.3% | 1.26x |

### Concurrency Issues (800 scenarios)
| Model | Success Rate | Improvement vs GPT-4 |
|-------|--------------|---------------------|
| Chronos | 58.3% | 18.2x |
| GPT-4.1 | 3.2% | - |
| Claude-4 | 2.8% | 0.88x |
| Gemini-2.0 | 4.1% | 1.28x |

### Memory Issues (600 scenarios)
| Model | Success Rate | Improvement vs GPT-4 |
|-------|--------------|---------------------|
| Chronos | 61.7% | 10.8x |
| GPT-4.1 | 5.7% | - |
| Claude-4 | 4.3% | 0.75x |
| Gemini-2.0 | 6.9% | 1.21x |

### API Misuse (900 scenarios)
| Model | Success Rate | Improvement vs GPT-4 |
|-------|--------------|---------------------|
| Chronos | 79.1% | 4.2x |
| GPT-4.1 | 18.9% | - |
| Claude-4 | 16.2% | 0.86x |
| Gemini-2.0 | 22.4% | 1.19x |

### Performance Bugs (400 scenarios)
| Model | Success Rate | Improvement vs GPT-4 |
|-------|--------------|---------------------|
| Chronos | 65.4% | 8.8x |
| GPT-4.1 | 7.4% | - |
| Claude-4 | 6.1% | 0.82x |
| Gemini-2.0 | 9.8% | 1.32x |

### Cross-Category (600 scenarios)
| Model | Success Rate | Improvement vs GPT-4 |
|-------|--------------|---------------------|
| Chronos | 51.2% | 12.5x |
| GPT-4.1 | 4.1% | - |
| Claude-4 | 3.7% | 0.90x |
| Gemini-2.0 | 5.2% | 1.27x |

## Repository Scale Performance

| Repository Size | Chronos | Best Baseline | Improvement |
|-----------------|---------|---------------|-------------|
| <10K LOC | 71.2% | 21.3% (Gemini) | 3.3x |
| 10K-100K LOC | 68.9% | 14.7% (Gemini) | 4.7x |
| 100K-1M LOC | 64.3% | 8.9% (Gemini) | 7.2x |
| >1M LOC | 59.7% | 3.8% (Gemini) | 15.7x |

## Statistical Significance

- **p-value**: < 0.001 (highly significant)
- **Cohen's d**: 3.87 (very large effect size)
- **95% CI for Chronos**: [65.2%, 69.4%]
- **Sample Size**: 5,000 scenarios

## Evaluation Methodology

All models evaluated on identical scenarios with:
- Multi-file context (10-50 files)
- Temporal dispersion (3-12 months)
- Obfuscated dependencies
- Real-world complexity

Last Updated: January 2025