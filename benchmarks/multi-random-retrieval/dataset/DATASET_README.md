# Chronos MRR Benchmark Dataset

## Important Notice

This directory contains a **representative sample** of the Kodezi Chronos Multi-Random Retrieval (MRR) benchmark dataset. 

**Full Benchmark Access:**
- The complete MRR benchmark contains 5,000 real-world debugging scenarios
- This sample includes 500 representative cases (10% of full benchmark)
- Full benchmark will be released Q1 2026 with the Chronos research publication
- For early access requests, contact: research@kodezi.com

## Dataset Structure

### Sample Dataset Files
- `mrr_sample_dataset.json` - 500 representative test cases
- `mrr_mini_dataset.json` - 50 cases for quick testing
- `example_bug.json` - Single detailed example

### Bug Categories Distribution (Sample)
| Category | Sample Cases | Full Benchmark |
|----------|--------------|----------------|
| Syntax Errors | 50 | 500 |
| Logic Errors | 120 | 1,200 |
| Concurrency Issues | 80 | 800 |
| Memory Issues | 60 | 600 |
| API Misuse | 90 | 900 |
| Performance Bugs | 40 | 400 |
| **Total** | **440** | **4,400** |

### Test Case Format
Each test case includes:
- Bug description and symptoms
- Repository snapshot reference
- Scattered context across multiple files
- Ground truth fix and validation criteria
- Temporal metadata (time spans, refactoring history)

## Why Sample Dataset?

1. **Reproducibility** - Allows researchers to validate methodology
2. **Development** - Enable tool development against realistic scenarios  
3. **Comparison** - Establish baseline performance metrics
4. **Learning** - Understand the complexity of real-world debugging

## Citation

When using this dataset, please cite:

```bibtex
@article{khan2025chronos,
  title={Kodezi Chronos: A Debugging-First Language Model},
  author={Khan, Ishraq and Chowdary, Assad and Haseeb, Sharoz and Patel, Urvish},
  journal={arXiv preprint arXiv:2507.12482},
  year={2025}
}
```

## License

This sample dataset is released under Apache 2.0 License.
Full benchmark terms will be provided upon release.