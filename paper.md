Kodezi Chronos: A Debugging-First Language Model for
Repository-Scale Code Understanding
Ishraq Khan, Assad Chowdary, Sharoz Haseeb, Urvish Patel, Yousuf Zaii
Kodezi Inc.
{Ishraq,Assad,Sharoz,Urvish,Yousuf}@kodezi.com
Abstract--- Debugging remains unsolved for LLMs despite
advances in code generation. While Claude Opus 4 and GPT4.1 achieve > 70% on synthesis benchmarks, they fail on real
debugging with < 15% success rates (95% CI: 12.1-17.9%). We
present Kodezi Chronos, the first debugging-specific language
model combining: (1) Adaptive Graph-Guided Retrieval (AGR)
navigating codebases up to 10M LOC via multi-hop traversal
(92% precision, 85% recall), (2) Persistent Debug Memory
(PDM) learning from 15M+ sessions, and (3) 7-layer architecture
for iterative fix-test-refine loops.
On 5,000 real-world scenarios, Chronos achieves 67.3%
± 2.1% fix accuracy versus 14.2% ± 1.3% (Claude 4) and
13.8% ± 1.2% (GPT-4.1), with Cohen's d=3.87 effect size.
The system reduces debugging time by 40% and iterations
by 65%. Chronos resolves complex multi-file bugs requiring
cross-repository understanding and temporal analysis.
Key limitations include 23.4% success on hardwaredependent bugs and 41.2% on dynamic language issues.
Theoretical analysis proves O(k log d) retrieval complexity
with convergence guarantees. Human evaluation (N=50) shows
89% preference over baselines. Available Q4 2025 (Kodezi OS)
and Q1 2026 (API).