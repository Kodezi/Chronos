# Contributing to Kodezi Chronos Research

Thank you for your interest in contributing to the Kodezi Chronos research repository! While the Chronos model itself is proprietary, we welcome contributions to improve our benchmarks, evaluation frameworks, and research documentation.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [What Can I Contribute?](#what-can-i-contribute)
- [Getting Started](#getting-started)
- [Contribution Process](#contribution-process)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

This project adheres to the [Kodezi Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@kodezi.com.

## What Can I Contribute?

### Welcome Contributions

- **Benchmark Improvements**: Enhance evaluation protocols or propose new metrics
- **Test Cases**: Submit real-world debugging scenarios for benchmarks
- **Documentation**: Improve clarity, fix errors, or add examples
- **Visualizations**: Create better ways to present results
- **Analysis Tools**: Build tools to analyze benchmark results
- **Research Extensions**: Propose extensions to our methodology

### Not Accepted

- Requests for model access (available only through Kodezi OS)
- Implementation details of proprietary algorithms
- Attempts to reverse-engineer the model
- Confidential or proprietary code examples

## Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/kodezi/chronos-research.git
   cd chronos-research
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Explore the Repository**
   - Read the [README.md](README.md)
   - Review existing benchmarks
   - Check open issues

## Contribution Process

### 1. Check Existing Work

Before starting:
- Search existing issues and PRs
- Review the project roadmap
- Join relevant discussions

### 2. Propose Your Contribution

For significant changes:
1. Open an issue describing your proposal
2. Wait for maintainer feedback
3. Proceed once approved

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 4. Make Your Changes

Follow our style guidelines and ensure:
- Code is well-documented
- Tests pass (if applicable)
- Documentation is updated

### 5. Submit a Pull Request

1. Push your branch to your fork
2. Create a PR with a clear description
3. Link related issues
4. Wait for review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] Added new tests (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## Style Guidelines

### Python Code

- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Keep functions focused and small

Example:
```python
def calculate_debug_success_rate(
    attempts: List[DebugAttempt],
    criteria: EvaluationCriteria
) -> float:
    """Calculate the success rate of debugging attempts.
    
    Args:
        attempts: List of debugging attempts to evaluate
        criteria: Criteria for determining success
        
    Returns:
        Success rate as a percentage (0-100)
    """
    successful = sum(1 for a in attempts if criteria.is_successful(a))
    return (successful / len(attempts)) * 100 if attempts else 0.0
```

### Documentation

- Use clear, concise language
- Include examples where helpful
- Keep formatting consistent
- Update table of contents

### Commit Messages

Format:
```
type(scope): brief description

Longer explanation if needed. Wrap at 72 characters.

Fixes #123
```

Types: feat, fix, docs, style, refactor, test, chore

## Review Process

### What to Expect

1. **Initial Review** (1-3 days)
   - Maintainers check alignment with project goals
   - Basic quality assessment

2. **Detailed Review** (3-7 days)
   - Code quality and style
   - Documentation completeness
   - Test coverage

3. **Iteration**
   - Address feedback
   - Update PR as needed

4. **Merge**
   - Squash and merge when approved
   - Delete branch after merge

### Review Criteria

- **Quality**: Is the code/documentation high quality?
- **Alignment**: Does it fit project goals?
- **Completeness**: Is it ready to merge?
- **Impact**: Does it improve the project?

## Community

### Getting Help

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: research@kodezi.com for research queries

### Recognition

Contributors are recognized in:
- Release notes
- Annual research report
- Conference presentations

## Research Ethics

When contributing:
- Respect intellectual property
- Maintain academic integrity
- Cite sources appropriately
- Follow responsible AI practices

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

## Questions?

If you have questions about contributing:
1. Check the [FAQ](docs/faq.md)
2. Search existing issues
3. Ask in GitHub Discussions
4. Email research@kodezi.com

Thank you for helping advance debugging AI research!