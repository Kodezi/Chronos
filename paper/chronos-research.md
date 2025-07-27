Kodezi Chronos: A Debugging-First Language Model for
Repository-Scale, Memory-Driven Code Understanding
Ishraq Khan, Assad Chowdary, Sharoz Haseeb, Urvish Patel
Kodezi Inc.
{Ishraq,Assad,Sharoz,Urvish}@kodezi.com
Abstract--- Large Language Models (LLMs) have advanced
code generation and software automation, but are fundamentally
constrained by limited inference-time context and lack of explicit
code structure reasoning. We introduce Kodezi Chronos [51], a
next-generation architecture for autonomous code understanding, debugging, and maintenance, designed to operate across
ultra-long contexts comprising entire codebases, histories, and
documentation---all without fixed window limits.
Kodezi Chronos leverages a multi-level embedding memory
engine, combining vector and graph-based indexing with
continuous code-aware retrieval. This enables efficient and
accurate reasoning over millions of lines of code, supporting
repository-scale comprehension, multi-file refactoring, and realtime self-healing actions.
Our evaluation introduces a novel Multi Random Retrieval
benchmark, specifically tailored to the software engineering
domain. Unlike classical retrieval benchmarks, this method
requires the model to resolve arbitrarily distant and obfuscated
associations across code artifacts, simulating realistic tasks such
as variable tracing, dependency migration, and semantic bug
localization. Chronos outperforms prior LLMs and code models--
-demonstrating a 23% improvement in real-world bug detection
and reducing debugging cycles by up to 40% compared to
traditional sequence-based approaches.
By natively interfacing with IDEs and CI/CD workflows,
Chronos enables seamless, autonomous software maintenance,
elevating code reliability and productivity while reducing manual
effort. These results mark a critical advance toward selfsustaining, continuously optimized software ecosystems.
I. INTRODUCTION
Recent advancements in large language models (LLMs)
have transformed code generation, review, and reasoning
tasks [1], [2], [10]. However, debugging---the most timeconsuming and critical aspect of software development---
remains largely unsolved. While tools like GitHub Copilot [11], Cursor, and Claude excel at code completion [12],
they fundamentally misunderstand debugging as a multifaceted, context-heavy process that spans entire repositories,
historical commits, CI/CD logs, and runtime behaviors. Production debugging requires reasoning across files separated
by thousands of lines [13], understanding temporal code
evolution, and correlating seemingly unrelated symptoms to
root causes buried deep in dependency chains [14].
Current code assistants fail at debugging for three critical
reasons: (1) they are trained primarily on code completion
tasks, not debugging workflows [15]; (2) they lack persistent
memory of past bugs, fixes, and codebase-specific patterns [16]; and (3) their context windows, even when extended
to 100K+ tokens, cannot capture the full debugging context
needed for complex, multi-file issues. Recent studies show
that even state-of-the-art models like GPT-4, Claude-3, and
Gemini-1.5 achieve less than 10% success rates on real-world
debugging benchmarks [17], [18], often proposing superficial
fixes that fail validation or introduce new regressions [19].
Kodezi Chronos represents a paradigm shift: the first
debugging language model developed by Kodezi [51], specifically designed, trained, and optimized for autonomous bug
detection, root cause analysis, and validated fix generation.
Unlike code completion models that generate syntactically
correct but often semantically flawed suggestions, Chronos
operates through a continuous debugging loop---proposing
fixes, running tests, analyzing failures, and iteratively refining solutions until validation succeeds. Built on a novel
architecture combining persistent debug memory, multisource retrieval (code, logs, traces, PRs), and execution
sandboxing, Chronos achieves what no existing model can:
true autonomous debugging at repository scale.
Chronos is designed for seamless integration with modern
development stacks: it operates as an embedded ‘‘AI CTO’’
within CI/CD pipelines, IDEs, and project management tools.
Its proactive, event-driven workflow ensures that debugging,
documentation generation, refactoring, and even preventative
maintenance actions occur autonomously, guided by deep
repository memory rather than manual prompts or brittle
heuristics.
To rigorously evaluate Chronos’s unique capabilities, we
move beyond traditional benchmarks and propose a multistep, random retrieval evaluation reflecting the authentic
complexities of code search, dependency resolution, and
semantic bug localization at scale. Empirically, Chronos
demonstrates state-of-the-art results across industry-standard
metrics and realistic maintenance tasks, reducing debugging
times and increasing project resilience.
This paper presents the architecture, memory system, retrieval mechanism, evaluation methodology, and experimental
results that establish Kodezi Chronos as the new frontier for
autonomous, ultra-contextual codebase management.
II. RELATED WORK AND LIMITATIONS OF
TRADITIONAL APPROACHES
The emergence of large-scale neural models for source code
processing---such as CodeBERT [46], GraphCodeBERT [4],
and CodeT5 [5]---has significantly advanced automatic code
synthesis, translation, and review. Many of these models, as
arXiv:2507.12482v1 [cs.SE] 14 Jul 2025
well as massive LLMs like GPT-3 and GPT-4 [1], [47], are
pre-trained on billions of lines of code paired with natural
language, learning rich semantic representations for many
programming languages.
Despite impressive gains on benchmark tasks, these
approaches are fundamentally bottlenecked by attentionbased architectures and fixed-size input windows, typically
constraining context to tens of thousands of tokens. Practical
developer workflows, by contrast, require tools to reason
across entire repositories: files, modules, historic commits,
documentation, and evolving build systems, far outstripping
standard context limits.
State-of-the-art retrieval-augmented generation (RAG)
methods extend practical context by embedding and recalling
external documents [8], but remain mostly limited to chunked
passage retrieval and lack true compositional, dependencyaware memory. Window expansion techniques---such as
models with 100k tokens or more [7]---incur prohibitive
compute/memory costs and suffer from diluted attention,
leading to information loss and degraded performance as
codebase size increases.
Existing benchmarks for long-context reasoning, like the
”Needle in a Haystack” pattern, commonly involve embedding
a salient but easily differentiable clue in a sea of noise
or repetition. Such evaluations unintentionally rely on the
model’s ability to match explicit tokens or unusual patterns,
providing only a partial test of true retrieval and reasoning
ability. In real-world maintenance, however, code elements
are frequently unmarked, distributed, and semantically interdependent, requiring the AI not just to ”find,” but to infer
context, resolve relationships, and reason about impact [45].
Other recent work explores graph neural networks (GNNs)
for modeling explicit data flow or control flow graphs [9],
[6]. While GNNs can capture structural properties of code,
they are rarely coupled with ultra-long context LLMs, and
lack the continuous learning, memory updating, and rapid
recall required for live autonomous maintenance.
Kodezi Chronos is motivated by these challenges: By combining continuous graph-aware indexing, dynamic embedding
updates, and reasoning-optimized memory retrieval, Chronos
transcends traditional limitations and enables truly repositoryscale, real-time software comprehension and intervention.
III. ARCHITECTURE OF KODEZI CHRONOS
A. The Output-Heavy Nature of Debugging
Despite the industry focus on ever-larger context windows
(128K, 200K, 1M+ tokens), debugging presents a fundamentally different challenge: it is inherently output-heavy rather
than input-heavy. This asymmetry has profound implications
for model design and optimization.
1) Input vs Output Token Distribution: What models
typically see (input):
• Error stack traces: 200-500 tokens
• Relevant source code: 1K-4K tokens
• Test failures and logs: 500-2K tokens
• Prior fix attempts: 500-1K tokens
• Total input: Often ¡10K tokens for most real-world
debugging tasks
What models must produce (output):
• Multi-file bug fixes: 500-1,500 tokens
• Root cause explanations: 300-600 tokens
• Updated unit tests: 400-800 tokens
• Commit messages/PR summaries: 150-300 tokens
• Documentation updates: 200-400 tokens
• Total output: Typically 2,000-4,000 tokens per debugging session
TABLE I
Input vs output characteristics in debugging tasks.
Aspect Input Context Output Generation
Nature Sparse, localized Dense, structured
Cost Impact Sublinear with retrieval Linear to exponential
Quality Limiter Retrieval precision Generation accuracy
Success Factor Context relevance Syntactic & semantic correctness
2) Why Output Quality Trumps Input Size: The critical
insight: a model with intelligent 8K context that generates
robust, test-passing fixes will outperform a 1M-context model
that produces syntactically correct but semantically flawed
patches.
3) Chronos’s Output-Optimized Architecture: Chronos
addresses this asymmetry through several architectural innovations:
1) Debug-Specific Generation Training: Unlike code
completion models trained on next-token prediction,
Chronos is trained on complete debugging sessions,
learning to generate structured fixes, explanations, and
tests as cohesive units.
2) Iterative Refinement Loop: Rather than single-shot
generation, Chronos validates outputs through execution, using test results to refine patches—ensuring
output quality over quantity.
3) Template-Aware Generation: Chronos learns
repository-specific patterns for commits, tests, and
documentation, reducing output token waste while
maintaining consistency.
4) Confidence-Guided Output: The model generates explanations and fallback strategies only when confidence
is below threshold, optimizing output token usage.
This output-centric design enables Chronos to achieve
65.3% debugging success despite competitors having 10-
100x larger context windows, validating that for debugging,
output quality and structure matter more than input capacity.
B. Core Architecture Overview
Kodezi Chronos is designed as an autonomous memorydriven intelligence layer for code, operating at scales that span
entire enterprise repositories, team histories, and auxiliary
knowledge sources. Its architecture consists of three core
modules: (i) a persistent Memory Engine for continuous graphbased context construction, (ii) an advanced Retriever that
dynamically assembles deep semantic context from code and
documentation, and (iii) a transformer-based Code Reasoning
Model for synthesis, debugging, and orchestration of software
changes.
Code, Docs,
CI/CD Logs
Memory Engine
(Embedding + Graph)
Multi-Code
Association Retriever
Reasoning Model
& Orchestration Test Results
Patches, Changelogs,
Test Results
Fig. 1. High-level overview of Chronos: Memory-driven embedding and
retrieval powering autonomous reasoning and codebase management.
Debugging Token Flow: Input vs Output
Input (Sparse)
Stack Trace: 300 tokens
Code Context: 2K tokens
Logs/Tests: 800 tokens
History: 500 tokens
Total: ∼3.6K tokens
Process
Output (Dense)
Bug Fix: 1.2K tokens
Explanation: 500 tokens
Tests: 600 tokens
Docs/PR: 400 tokens
Fallback: 300 tokens
Total: ∼3K tokens
Key Insight: Output ≈ Input in debugging
Quality matters more than quantity
Fig. 2. Token distribution in debugging tasks: Unlike typical LLM
applications where input dominates, debugging requires substantial, highquality output generation.
C. Memory Engine: Repository-Scale Embedding and Indexing
The Memory Engine is responsible for ingesting, encoding,
and maintaining a unified semantic representation of all
project files, versioned code, documentation, configuration,
historical diffs, test outcomes, and architectural artifacts. Each
unit of code (e.g., function level, file, commit) is parsed
to extract both sequence and structural cues---using ASTs,
dependency graphs, and metadata links.
These elements are then projected into a high-dimensional
vector space via context-aware, code-specific encoders trained
on multiple programming languages and coding paradigms.
The Memory Engine stores not just static embeddings but
also maintains an evolving graph database, where nodes
represent code elements and edges denote code relationships
(e.g., function calls, module imports, bug-ticket links, commit
ancestry).
login.py auth utils.py
README.md
test login.py
bug 1234.md
calls
cited in
linked bug in
tested by
Fig. 3. Graph-structured memory indexing in Kodezi Chronos: code,
documentation, and test elements as nodes, with functional relationships as
edges.
This design enables Chronos to efficiently retrieve, traverse,
and reason about segments of the codebase that share nonlocal relationships, even if separated by thousands of lines,
multiple files, or extensive revision history.
D. Achieving Unlimited Context Through Smart Retrieval
Traditional LLMs are fundamentally constrained by attention complexity and memory limitations. Even models
claiming ”unlimited” context achieve this through sliding
windows or hierarchical attention that loses critical debugging
information. Chronos implements true unlimited context
through:
• Hierarchical Code Embeddings: Multi-level representations from token → statement → function → module
→ repository
• Temporal Context Indexing: Every code element
tagged with commit history, allowing time-travel debugging
• Semantic Dependency Graphs: Explicit modeling of
import chains, inheritance hierarchies, and data flows
• Dynamic Context Assembly: At inference, retrieves
precisely the code paths relevant to the current bug
This approach enables Chronos to maintain full repository
awareness while operating within reasonable computational
bounds---a critical requirement for production deployment.
E. Deep Context Retrieval and Multi-Code Association
Chronos utilizes a novel multi-code compositional retrieval
mechanism, powered by AGR, purpose-built for software
engineering. Upon each reasoning or generation request---
such as ”fix a failing test,” ”refactor authentication logic,”
or ”explain API drift”---the Adaptive Retrieval Engine
dynamically assembles a tailored context window by:
• Issuing semantic queries to the Memory Engine that
leverage both metric similarity and structural navigation
in the code graph, with dynamic depth expansion (k-hop)
based on query complexity.
• Associating multiple code artifacts through typed relationships: e.g., tracing variable definitions across
documentation (k=1), implementation (k=2), regression
tests (k=2), and historic bug reports (k=3), stopping
when confidence exceeds 90% or diminishing returns
detected.
• Dynamically refining the context through intermediate
model inferences and confidence scoring, adapting
retrieval depth in real-time. Complex debugging queries
automatically trigger deeper graph traversal (k=3-5),
while simple lookups terminate at k=1-2.
• Utilizing edge type priorities: implementation edges
(weight=1.0), dependency edges (weight=0.8), documentation edges (weight=0.6), ensuring most relevant paths
are explored first.
TABLE II
Example multi-code association retrieval: constructing a
task-specific context window for a bug fix.
Step Retrieved Entity Relationship
Q1 login.py Direct bug context
Q2 test login.py Linked test
Q3 settings.py Imported env vars
Q4 bug 1234.md Historical bug doc
Q5 commit a1b2c3 Last related commit
This approach allows Chronos to reason across arbitrarily
distant, compositionally linked code and documentation
artifacts---precisely what is needed for complex debugging,
cross-module dependencies, or audit trails.
F. Adaptive Graph-Guided Retrieval (AGR)
Traditional flat retrieval approaches fail to capture the
intricate relationships between code artifacts, leading to
incomplete context and erroneous fixes. Chronos introduces
Adaptive Graph-Guided Retrieval (AGR), a dynamic
mechanism that intelligently expands retrieval neighborhoods
based on query complexity and confidence thresholds.
1) Iterative Context Expansion: The AGR mechanism
operates through iterative k-hop neighbor expansion:
1) Initial Query Analysis: Decompose the debugging
request into semantic components and identify seed
nodes in the code graph
2) Adaptive Depth Determination: Calculate optimal
retrieval depth based on:
• Query complexity score (0-1)
• Code artifact density in the neighborhood
• Historical debugging patterns for similar issues
3) Guided Expansion: Follow typed edges (implementation, dependency, dataflow) to retrieve contextually
relevant nodes
4) Confidence-Based Termination: Stop expansion when
retrieval confidence exceeds threshold or diminishing
returns detected
2) Graph-Guided vs Traditional Planning: Our empirical
analysis reveals fundamental differences between traditional
LLM planning and AGR-enhanced debugging:
Traditional LLM Planning
Query: Implement state machine
state <= `d<0> > S
S () <-d<0> > S
Traditional Steps:
1. Define Module Interface
2. Define State Encoding
3. State Transition Logic
4. Output Logic: Assign outputs
Issues:
- High-level plans without task details
- Hard to follow implementation
- Lost signal/transition specs
Generated Code:
assign S next = (state == 5’b11010) ?
5’b11010 : (state == 5’b10110) ?
5’b11010 : state;
× Incorrect implementation
AGR-Enhanced Debugging
Query: Implement state machine
+ Graph retrieval of specifications
+ Signal transition examples
AGR-Guided Steps:
1. Retrieve signal definitions (k=1)
2. Expand to transitions (k=2)
3. Include test examples (k=3)
Retrieved Context:
- S1 next: Output signal
- Wait->S, S->S transitions
- Example: 9’b101000100
Generated Code:
// Correct implementation
assign S1 next = S;
// Based on retrieved specs
✓ Verified correct
23% Success Rate 87% Success Rate
Fig. 4. Traditional LLM planning vs AGR-enhanced debugging: Graphguided retrieval provides complete context, leading to accurate implementations.
k=1: Initial Retrieval
Plan
Signal
Impl
Trans
Ex1 Ex2
Retrieved:
S1 next: Output signal
(Type: Signal)
k=2: Expanded Retrieval
Plan
Signal
Impl
Trans
Ex1 Ex2
State Wait
Doc Test
Additional Retrieved:
State transitions: Wait-¿S1
Example: 9’b101000100100
Confidence: 92%
Legend: Query k=1 k=2 Not Retrieved
Fig. 5. Iterative context expansion in Adaptive Graph-Guided Retrieval:
Starting from a query node, the system progressively expands retrieval depth
(k-hops) based on confidence thresholds and query complexity.
Bug
Vector AST Graph History
Retriever
Ranker
Source Tests Fixes Logs
Fig. 6. Multi-modal retrieval mechanism in Chronos.
G. Reasoning, Generation, and Autonomous Orchestration
The transformer-based Chronos Reasoning Model operates
directly over the retrieved, multi-source debugging context.
Unlike classical code completion models, Chronos:
• Diagnoses root causes and synthesizes code changes
conditioned on project documentation, prior commits,
and dependency patterns.
• Produces stepwise fix plans, code diffs, documentation
updates, and regression test suggestions in a unified,
automated debugging loop.
• Orchestrates a full debugging workflow: proposes bug
fixes, invokes relevant tests, parses results, iterates on
failures, and generates changelogs or PR summaries---all
autonomously.
All outputs and feedback streams (test results, reviewer
comments, CI/CD events) are fed back into the Memory
Engine, enabling lifelong refinement and rapid adaptation to
new debugging scenarios.
This cyclic process of context assembly, reasoning, autonomous validation, and memory update is the core of
Chronos’s persistent codebase intelligence, enabling selfsustaining and ever-improving debugging at scale.
Autonomous Code/
Documentation Generation
(Bug Fix Proposal)
Automated
Testing & Validation
Memory Update Iterative Plan
Refinement
Test Passed Test Failed
Reviewer Feedback CI/CD Events
Fig. 7. Chronos debugging feedback loop: Automated bug fix generation,
validation, plan refinement, and memory update for continuous autonomous
improvement.
IV. THE DEBUGGING LANGUAGE MODEL PARADIGM
Kodezi Chronos fundamentally departs from traditional
code models by being purpose-built as a debugging language
model---the first of its kind. While existing LLMs treat
debugging as a code generation problem, Chronos recognizes
it as a complex, iterative process requiring specialized
capabilities, training, and architecture.
A. Core Architectural Layers
Chronos implements a revolutionary 7-layer architecture
specifically designed for autonomous debugging:
1) Multi-Source Input Layer: Ingests heterogeneous
debugging signals including source code, CI/CD logs,
error traces, stack dumps, configuration files, historical
PRs, and issue reports. Unlike code models that primarily process source files, Chronos natively understands
debugging artifacts.
2) Adaptive Retrieval Engine: Employs AGR (Adaptive
Graph-Guided Retrieval) with a hybrid vector-symbolic
approach combining:
• Dynamic k-hop neighbor expansion based on query
complexity
• AST-aware code embeddings that preserve structural relationships
• Dependency graph indexing for cross-file impact
analysis
• Call hierarchy mapping for execution flow understanding
• Temporal indexing of code evolution and bug
history
• Confidence-based termination for optimal context
assembly
3) Debug-Tuned LLM Core: A transformer architecture
specifically fine-tuned on debugging workflows, not
just code completion. Training tasks include:
• Root cause prediction from symptoms
• Multi-file patch generation
• Test failure interpretation
• Regression risk assessment
4) Orchestration Controller: Implements the autonomous
debugging loop:
• Hypothesis generation from error signals
• Iterative fix refinement based on test results
• Rollback mechanisms for failed attempts
• Confidence scoring for proposed solutions
5) Persistent Debug Memory: Maintains long-term
knowledge including:
• Repository-specific bug patterns and fixes
• Team coding conventions and preferences
• Historical fix effectiveness metrics
• Module-level vulnerability profiles
6) Execution Sandbox: Real-time validation environment
supporting:
• Isolated test execution
• CI/CD pipeline emulation
• Performance regression detection
• Security vulnerability scanning
7) Explainability Layer: Generates human-readable outputs:
• Root cause explanations with evidence chains
• Fix rationale documentation
• Automated PR descriptions and commit messages
• Risk assessment reports
B. Training on Debugging Workflows
Unlike models trained primarily on code completion,
Chronos’s training regime focuses exclusively on debugging
scenarios:
Pre-training Corpus:
• 15M+ GitHub issues with linked PRs and fix commits
• 8M+ stack traces paired with resolutions
• 3M+ CI/CD logs from failed and fixed builds
• Production debugging sessions from enterprise partners
• Open-source bug databases (Defects4J, SWE-bench,
BugsInPy)
Specialized Fine-tuning Tasks:
• Chain-of-Cause Reasoning: Teaching the model to trace
error propagation through call stacks and dependencies [49]
• Multi-Modal Bug Understanding: Correlating code, logs,
traces, and documentation
• Iterative Fix Refinement: Learning from failed fix
attempts to improve subsequent proposals [50], [48]
• Cross-Repository Pattern Recognition: Identifying similar bugs across different codebases
C. The Autonomous Debugging Loop
Chronos’s debugging loop represents a fundamental innovation over single-shot code generation:
Detect Issue
Retrieve Context
Propose Fix
Run Tests
Refine Strategy Tests Pass? Commit & Deploy
Update Memory
No Yes
Fig. 8. The Chronos autonomous debugging loop: continuous iteration
until validation succeeds.
This loop continues autonomously, with each iteration
informed by previous attempts and accumulated knowledge,
until a validated fix is achieved or human intervention is
requested.
V. EVALUATION METHODOLOGY
To rigorously assess Kodezi Chronos’s capabilities across
realistic debugging and maintenance workflows, we adopt a
multi-faceted evaluation strategy that goes beyond conventional sequence completion or shallow retrieval tests.
A. Benchmarking Datasets and Tasks
Chronos is evaluated on a diverse suite of benchmarks,
comprising:
• Standard Code Generation Benchmarks: HumanEval [2], MBPP [3], and related tasks for basic
code synthesis and function-level reasoning.
• Repository-Scale Debugging Tasks: A curated set
of real-world bug reports, failing test scenarios, and
codebase refactoring challenges drawn from open-source
projects and industry case studies.
• Multi-Code Association Retrieval: Custom synthetic
benchmarks requiring retrieval and reasoning across
arbitrarily placed, subtly linked code/documentation
artifacts---simulating variable tracing, cross-file bug
localization, or dependency update chains.
B. Multi-Code Reasoning Evaluation Protocol
Unlike traditional benchmarks that target token-level prediction in narrow context, our protocol explicitly:
• Randomizes the placement of relevant context (bug
source, documentation clue, test assertion) across large
codebases and histories.
• Requires Chronos to retrieve, associate, and utilize
multi-code context in a compositional manner, solving
tasks that demand reasoning over both explicit code
relationships (e.g., function calls, imports) and implicit
bug/error propagation patterns.
• Measures both retrieval accuracy (whether Chronos
finds all necessary context) and end-to-end task success
(whether it can autonomously fix, validate, and document
the issue).
C. Multi Random Retrieval Benchmark
We introduce the Multi Random Retrieval (MRR)
benchmark, specifically designed to evaluate debuggingoriented retrieval capabilities:
1) Benchmark Design: The MRR benchmark consists of
5,000 real-world debugging scenarios where:
1) Context Scattering: Relevant debugging information
is randomly distributed across 10-50 files
2) Temporal Dispersion: Critical bug context spans 3-12
months of commit history
3) Obfuscated Dependencies: Variable names and function calls are refactored between bug introduction and
discovery
4) Multi-Modal Artifacts: Solutions require combining
code, tests, logs, and documentation
2) Evaluation Metrics:
• Retrieval Precision@k: Fraction of retrieved artifacts
that are relevant to the bug fix
• Retrieval Recall@k: Fraction of all relevant artifacts
successfully retrieved
• Fix Accuracy: Whether the generated fix passes all tests
and doesn’t introduce regressions
• Context Efficiency: Ratio of used vs retrieved tokens
in the final solution
TABLE III
Performance on Multi Random Retrieval benchmark, demonstrating
Chronos’s superior ability to find and utilize scattered debugging
context.
Model Precision@10 Recall@10 Fix Accuracy Context Eff.
GPT-4 + RAG 42.3% 31.7% 8.9% 0.23
Claude-3 + Vector DB 48.1% 36.2% 11.2% 0.28
Gemini-1.5 + Graph 51.7% 41.8% 14.6% 0.31
Kodezi Chronos 89.2% 84.7% 67.3% 0.71
3) Results on MRR Benchmark:
D. Adaptive Graph-Guided Retrieval Performance
We evaluate the impact of AGR on debugging accuracy
across different retrieval depths:
TABLE IV
Performance metrics for different retrieval strategies. Adaptive
AGR dynamically selects optimal k based on query complexity.
Retrieval Method k=1 k=2 k=3 k=adaptive Flat
Precision 84.3±2.1% 91.2±1.4% 88.7±1.8% 92.8±1.2% 71.4±3.2%
Recall 72.1±2.8% 86.4±1.9% 89.2±1.6% 90.3±1.5% 68.2±3.5%
F1 Score 77.7±2.4% 88.7±1.6% 88.9±1.7% 91.5±1.3% 69.8±3.3%
Debug Success 58.2±3.1% 72.4±2.3% 71.8±2.4% 87.1±1.8% 23.4±4.1%
Key findings from AGR evaluation:
• Optimal Depth Varies: Simple bugs require k=1-2,
while complex cross-module issues benefit from k=3+
• Adaptive Superiority: Dynamic depth selection outperforms fixed k values by 15-20%
• 5x Improvement: AGR achieves 87.1% debug success
vs 23.4% for flat retrieval
• Hardware Debugging: Particularly effective for Verilog/VHDL with 91% accuracy (vs 18% baseline)
Model HumanEval MBPP Debug Success Root Cause Acc. Retrieval Prec.
GPT-4 85.7±1.2% 87.0±0.9% 8.5±2.1% 12.3±1.8% 68±2.3%
GPT-4-Turbo 87.1±1.0% 88.2±0.8% 9.2±1.9% 14.1±1.6% 71±2.0%
Claude-3-Opus 84.9±1.3% 86.1±1.1% 7.8±2.3% 11.7±2.0% 67±2.4%
Claude-3-Sonnet 83.2±1.4% 85.2±1.2% 7.3±2.4% 10.9±2.1% 66±2.5%
Gemini-1.5-Pro 88.3±0.9% 89.1±0.7% 11.2±1.7% 15.8±1.5% 74±1.8%
CodeT5+ 86.5±1.1% 84.8±1.3% 10.6±1.8% 13.2±1.7% 72±1.9%
Chronos 90.2±0.6%*** 88.9±0.5%* 65.3±1.4%*** 78.4±1.2%*** 91±0.8%***
*p ¡ 0.05, **p ¡ 0.01, ***p ¡ 0.001 compared to best baseline (two-tailed t-test)
TABLE V
Performance across code synthesis and debugging tasks (mean ± std
over 5 runs). Statistical significance shown.
E. Comparison with Agentic Code Tools
While traditional LLMs struggle with debugging, a new
generation of agentic code tools has emerged. We evaluate
Chronos against these systems on real-world debugging
scenarios:
Tool Context Memory Debug Loop Multi-File CI/CD Success Rate
Cursor Auto IDE only None No Limited No 4.2%
Claude Code 200K tokens Session No Yes No 6.8%
OpenAI Codex 8K tokens None No No No 3.1%
Gemini CLI 1M tokens None No Yes Limited 9.7%
GitHub Copilot X 16K tokens None No Limited No 5.3%
Chronos Unlimited* Persistent Yes Yes Yes 65.3%
TABLE VI
Comparison of Chronos with agentic code tools. *Unlimited via
intelligent retrieval and memory.
Key differentiators of Chronos:
• Persistent Memory: Unlike session-based tools,
Chronos maintains cross-session knowledge of bugs,
fixes, and patterns
• True Debugging Loop: Automated iteration through
fix-test-refine cycles until validation succeeds
• CI/CD Integration: Native understanding of build
systems, test frameworks, and deployment pipelines
• Unlimited Context: Smart retrieval enables reasoning
over entire repositories without token limits
F. Cycle-Aware Debugging Case Study
To showcase Chronos’s real-world debugging prowess, we
conduct a qualitative study involving a set of regression bug
scenarios drawn from a large open-source Python project.
Metrics include:
• Number of attempts to converge on a passing code/test
cycle.
• Ability to document and explain root causes compared
to human reviewers.
• Time-to-resolution and reduction in manual engineering
effort.
GPT-4 Claude CodeT5+ Chronos
0
2
4
6
8
6.5
6.8
5.1
2.2
Model
Avg. Cycles to Fix
Fig. 9. Average code-to-fix cycles for Chronos and baseline models on
real-world bugs (lower is better).
Chronos demonstrates not only higher accuracy and retrieval precision, but also a dramatically reduced number
of debug cycles---underscoring its benefit for continuous,
automated codebase reliability.
G. Case Studies
To illustrate Chronos’s debugging capabilities, we present
two real-world examples from our evaluation:
1) Case Study 1: Cross-Module Null Pointer Exception:
Bug Report: ”Application crashes with NullPointerException
when processing user exports after recent authentication
refactor”
Chronos Reasoning Process:
1) Retrieved recent commits mentioning ”authentication”
(found 3 relevant commits)
2) Traced data flow from auth module to export module
3) Identified missing null check after auth token refresh
4) Located similar pattern in 2 other modules
Generated Fix:
Null Pointer Fix in Authentication Flow
// In AuthService.java
public AuthToken refreshToken (String userId) {
AuthToken token = tokenCache .get(userId);
if (token == null || token. isExpired ()) {
token = authProvider . generateToken (userId);
+ if (token != null) {
+ tokenCache.put(userId, token);
+ }
}
return token;
}
// In ExportService.java
public void exportUserData (String userId) {
AuthToken token = authService . refreshToken (userId);
+ if (token == null) {
+ throw new AuthenticationException(
+ "Failed to authenticate user for export");
+ }
// ... rest of export logic
}
Validation Results: All 47 test cases passed, including 3
new tests Chronos generated for the edge case.
2) Case Study 2: Async Race Condition in Message
Queue: Bug Report: ”Intermittent message loss in highload scenarios, approximately 0.1% messages not processed”
Chronos Analysis:
• Retrieved message queue implementation and recent
load test results
• Identified race condition between acknowledgment and
connection pooling
• Found similar issue fixed 8 months ago in different
component
• Applied analogous solution with adaptations
Generated Fix:
Race Condition Fix in Message Queue
// MessageProcessor.java
private void processMessage (Message msg) {
try {
handler.process(msg);
- connectionPool.returnConnection(conn);
- msg.acknowledge();
+ // Fix: Acknowledge before returning connection
+ msg.acknowledge();
+ connectionPool.returnConnection(conn);
} catch ( Exception e) {
+ // Ensure connection returned even on error
+ connectionPool.returnConnection(conn);
msg.nack ();
throw e;
}
}
Results: Load test with 10M messages showed 0
H. Long-Context Debugging Performance
Even models with extended context windows fail at real
debugging tasks due to fundamental architectural limitations:
Model Context Size Cross-File Bugs Historical Bugs Complex Traces Avg. Success
GPT-4-32K 32K tokens 7.2±1.9% 3.1±1.2% 5.8±1.6% 5.4±1.5%
Claude-3-200K 200K tokens 9.8±2.1% 4.7±1.4% 8.3±1.8% 7.6±1.7%
Gemini-1.5-Pro-1M 1M tokens 14.3±2.3% 6.2±1.5% 11.7±2.0% 10.7±1.9%
Chronos Unlimited 71.2±1.8%*** 68.9±2.0%*** 74.3±1.6%*** 71.5±1.8%***
***p ¡ 0.001 compared to Gemini-1.5-Pro-1M (paired t-test, n=100 tasks per category)
TABLE VII
Performance on debugging tasks requiring extensive context.
Statistical significance demonstrates retrieval superiority.
The results demonstrate that raw context size alone cannot
solve debugging. Chronos’s intelligent retrieval, persistent
memory, and debug-specific training enable it to outperform
even million-token models by over 6x.
I. Detailed Performance Analysis
We further analyze Chronos’s performance across different
bug categories and complexity levels:
Bug Category Syntax Logic Concurrency Memory API Performance
GPT-4 82.3% 12.1% 3.2% 5.7% 18.9% 7.4%
Claude-3-Opus 79.8% 10.7% 2.8% 4.3% 16.2% 6.1%
Gemini-1.5-Pro 85.1% 15.3% 4.1% 6.9% 22.4% 9.8%
Chronos 94.2% 72.8% 58.3% 61.7% 79.1% 65.4%
TABLE VIII
Success rates by bug category. Chronos shows particular strength
in complex bug types that require deep understanding.
Repository Size ¡10K LOC 10K-100K 100K-1M ¿1M LOC
GPT-4 15.2% 9.8% 4.3% 1.2%
Claude-3-200K 17.8% 11.2% 5.7% 2.1%
Gemini-1.5-Pro 21.3% 14.7% 8.9% 3.8%
Chronos 71.2% 68.9% 64.3% 59.7%
TABLE IX
Debugging success rates by repository size, demonstrating Chronos’s
scalability.
J. Multi-Code Association Retrieval Performance
We evaluate Chronos’s ability to retrieve and associate
multiple code artifacts for debugging:
Retrieval Task Precision Recall F1 Score
Variable Tracing 92.3±1.4% 89.7±1.6% 91.0±1.2%
Cross-File Dependencies 88.9±1.8% 91.2±1.5% 90.0±1.4%
Historical Bug Patterns 94.1±1.1% 87.3±2.0% 90.6±1.3%
Test-Code Mapping 91.7±1.3% 93.5±1.2% 92.6±1.0%
Documentation Links 85.4±2.1% 88.9±1.9% 87.1±1.7%
Average 90.5±0.8% 90.1±0.9% 90.3±0.7%
TABLE X
Multi-code association retrieval performance across different
debugging contexts.
K. Computational Efficiency
A critical consideration for production deployment is
computational efficiency. We analyze Chronos’s performance
characteristics compared to baselines and human debugging:
Metric GPT-4 Claude-3 Gemini-1.5 Chronos Human Dev
Avg. Time to Fix 82.3s 76.9s 71.2s 134.7s 2.4 hours
Context Window 128K tokens 200K tokens 1M tokens Unlimited* N/A
Cost per Bug $0.47 $0.52 $0.68 $0.89 $180
Success Rate 8.5% 7.8% 11.2% 65.3% 94.2%
Effective Cost* $5.53 $6.67 $6.07 $1.36 $191
*Unlimited via dynamic retrieval; Effective cost = Cost per bug / Success rate
TABLE XI
Computational efficiency and cost analysis. Despite higher
per-attempt cost, Chronos’s high success rate yields lowest effective
cost.
1) Inference Time Breakdown: Chronos’s 134.7s average
debugging time consists of:
• Context Retrieval: 23.4s (17.4%)
• Multi-round Reasoning: 67.8s (50.3%)
• Test Execution: 31.2s (23.2%)
• Memory Update: 12.3s (9.1%)
2) Return on Investment Analysis: For a typical enterprise
with 100 developers:
• Annual debugging time: 150,000 hours
• Chronos automation potential: 65.3% × 150,000 = 97,950
hours
• Cost savings: 97,950 × $90/hour - deployment costs =
$8.1M annually
• ROI: 47:1 in first year, accounting for infrastructure and
licensing
VI. DISCUSSION AND ABLATION ANALYSIS
A. Qualitative Insights
Our evaluation highlights several domains where Chronos
delivers outsized impact compared to prior systems:
• Holistic Bug Localization: Chronos traces complex
error origins across modules, commits, and documentation with no manual guidance, routinely identifying root
causes overlooked by token-limited models.
• Autonomous Debugging Loops: Chronos adapts its
retrieval and patching behavior over multiple test cycles,
integrating failed test feedback and reviewer commentary
to iteratively refine solutions.
• Continuous Knowledge Incorporation: By feeding
CI/CD, reviewer, and test feedback into persistent memory, Chronos improves its project-specific performance
over time, exhibiting lower repeated error rates and faster
adaptation to new code patterns.
Bug Scenario GPT-4 Chronos Chronos Resolution Path
Test Failure on user auth Incorrect var patch Full fix Traced import drift → found stale config →
auto-fix and doc update
API Deprecation Missed call-site Full fix Multi-code association retrieved usage in 3 files,
migrated all refs
Intermittent CI Error Flaky retry logic Full fix Ingested CI logs, patched async boundary, added
test case and explanation
TABLE XII
Qualitative examples where Chronos successfully applies multi-code
context to resolve debugging tasks beyond the reach of baseline
LLMs.
B. Ablation Studies
To isolate the contribution of core design features, we
perform targeted ablations:
• No Multi-Code Association: When Chronos is restricted
to single-chunk retrieval, debug success falls by 45%
and retrieval precision drops sharply, mirroring the
limitations of prior RAG pipelines.
• Static Memory Only: If the live feedback/memory
update mechanism is ablated (i.e., only static embeddings
used), adaptivity stagnates, and repeated bug classes
recur more often.
• No Orchestration Loop: Disabling the validate-retrieveupdate workflow reverts performance to basic code
suggestion with higher error rate and longer time-tofix.
Full No MCA Static No Orch
0
20
40
60
80
100 90
49
62
55
Configuration
Debug Success (%)
Fig. 10. Ablation analysis: Debugging success rate with each Chronos core
component removed (lower is worse).
These findings underscore the essential synergy between
deep memory, multi-code contextualization, and autonomous
workflow orchestration for effective debugging and adaptive
code maintenance.
C. Failure Analysis
Despite Chronos’s strong performance, our analysis reveals
specific failure modes and bug categories where the system
struggles:
1) Common Failure Modes:
1) Hardware-Dependent Bugs: Chronos achieves only
23.4% success on bugs requiring hardware-specific
knowledge (e.g., GPU memory alignment, embedded
system timing). Example failure:
Bug: CUDA kernel crashes with unaligned memory
access on Tesla V100
Chronos Fix: Added boundary checks (incorrect)
Correct Fix: Aligned memory allocation to 128-byte
boundaries
2) Distributed System Race Conditions: Complex
timing-dependent bugs across multiple services show
31.2% success rate. The model struggles to reason
about non-deterministic execution orders across network
boundaries.
3) Domain-Specific Logic Errors: Bugs requiring deep
domain knowledge (medical, financial regulations)
succeed only 28.7% of the time. Example:
Bug: HIPAA compliance violation in patient data export
Issue: Chronos lacks healthcare regulatory knowledge
2) Edge Cases and Limitations:
• Extremely Large Monorepos (¿10M LOC): Performance degrades to 45.3% success rate due to retrieval
precision issues
• Legacy Code with Poor Documentation: Success drops
to 38.9% when code lacks comments and uses cryptic
variable names
• Multi-Language Polyglot Systems: Cross-language
bugs (e.g., Python calling Rust via FFI) show only 41.2%
success
• UI/UX Bugs: Visual rendering issues essentially unsolvable (8.3% success) without screenshot analysis
Bug Category Success Rate Primary Failure Reason
Hardware-Specific 23.4±3.2% Lacks hardware specs
Distributed Race 31.2±2.8% Non-deterministic timing
Domain Logic 28.7±3.1% Missing domain knowledge
Legacy Code 38.9±2.9% Poor code quality
Cross-Language 41.2±2.7% FFI complexity
UI/Visual 8.3±1.9% No visual understanding
TABLE XIII
Chronos performance on challenging bug categories.
VII. LIMITATIONS, FUTURE WORK, AND BROADER
IMPACT
A. Current Limitations
While Chronos marks a significant advance in autonomous
code maintenance, certain limitations remain:
• Extreme-Scale Context Latency: Despite highly efficient memory and retrieval, performance can be constrained in ultra-large monolithic repositories during peak
concurrent update hours.
• Initial Memory Cold Start: Brand new projects (no
history) or projects with very sparse documentation
may exhibit reduced multi-code association richness,
necessitating a brief period of active learning.
• Non-Determinism and Overcorrection: In some edge
cases, especially with noisy historical feedback, Chronos
has shown a tendency to ”over-correct” or introduce
minor regressions before self-stabilization.
• Opaque Reasoning Pathways: The fully autonomous
nature and integration of deep learning sometimes hinder
model explainability, which may limit adoption in highly
regulated or safety-critical industries.
B. Future Work
We are actively addressing these limitations and have
several concrete directions for improvement:
• Incremental Embedding Optimization: Research into
hybrid memory systems and smarter incremental reindexing to further minimize retrieval and context
assembly latency during scale-out operations.
• Interactive and Visual Explanations: Implementation
of stepwise reasoning visualizers and debug trace replays,
making Chronos’ decision process more transparent to
engineers and auditors.
• Multi-Project/Organization Federated Memory: Extending Chronos memory to operate across multiple
repositories and organizational boundaries, supporting
federated bug detection, code migration, and systemic
risk profiling.
• Human-in-the-Loop Collaboration: Exploring adaptive
workflows where engineers and Chronos can jointly
control the loop—overriding, annotating, or confirming
automated fixes in sensitive code regions.
• Security and Adversarial Robustness: Building rigorous defense mechanisms against prompt injection,
memory poisoning, and adversarial debugging cases.
C. Deployment Architecture and Integration
The proposed architecture extends beyond isolated debugging to comprehensive autonomous maintenance through
a multi-tiered system design. The integration framework
comprises:
• Continuous Monitoring Layer: Real-time analysis
of code quality metrics, security vulnerability patterns,
and performance degradation indicators using static and
dynamic analysis techniques
• Automated Dependency Resolution: Graph-based impact analysis for dependency updates with probabilistic
risk assessment and automated rollback mechanisms
• Self-Healing Pipeline Integration: Event-driven architecture for autonomous incident response, incorporating
validated patches into existing CI/CD workflows
• Knowledge Synthesis Module: Automated extraction
and formalization of implicit domain knowledge through
documentation generation and code pattern analysis
Our empirical studies indicate that such integrated deployment can reduce mean time to resolution (MTTR) by 67%
while maintaining a false positive rate below 3%. Field trials
with industry partners are ongoing to validate these findings
at scale.
D. Broader Impact
By enabling persistently self-healing and context-aware
code maintenance, Chronos aims to shift an industry paradigm:
reducing human toil and repetitive bug resolution, freeing
engineers to focus on architecture, innovation, and user
demands. As we scale deployment, it is crucial to steward
responsible AI governance, data privacy, and an inclusive
transition for developer workforces worldwide.
VIII. CONCLUSION
We have presented Chronos, a novel debugging-specific
language model that addresses fundamental limitations in
existing code understanding systems. Through specialized
training on debugging workflows and a purpose-built architecture incorporating persistent memory and intelligent retrieval,
Chronos demonstrates significant improvements over generalpurpose language models in automated debugging tasks.
Our comprehensive evaluation reveals that Chronos
achieves a 65.3% success rate on real-world debugging
benchmarks, representing a 6-7x improvement over stateof-the-art models including those with million-token contexts.
This performance gain is attributed to three key technical
contributions: (1) domain-specific pre-training on 15 million
debugging instances including stack traces, fix commits,
and CI/CD logs, (2) a persistent memory architecture that
maintains cross-session knowledge of project-specific patterns,
and (3) a hierarchical retrieval mechanism that enables
effective reasoning over repository-scale contexts without
computational constraints.
The implications of this work extend beyond immediate
debugging applications. By demonstrating that specialized
architectures and training regimes can dramatically improve
performance on complex software engineering tasks, we
provide evidence for the viability of task-specific language
models in technical domains. Future research directions
include extending this approach to other software engineering
workflows, investigating transfer learning between debugging
domains, and exploring human-AI collaborative debugging
frameworks.
The transition toward autonomous debugging systems
raises important considerations regarding software quality
assurance, developer skill evolution, and the changing nature
of software maintenance. As these systems mature, careful
attention must be paid to maintaining human oversight,
ensuring explainability of automated fixes, and preserving the
creative and architectural aspects of software development
that remain fundamentally human endeavors.
The Chronos model will be available in Q4 of 2025 and
deploy on Kodezi [51] OS Q1 2026. This timeline allows for
additional safety testing, enterprise integration development,
and establishment of responsible deployment guidelines.
ACKNOWLEDGMENTS
Acknowledgments
This work benefited from the feedback and real-world
challenges shared by early-access engineering partners, enterprise pilot users, and the broader Kodezi community. The
maintainers of open-source repositories and tooling enabled
large-scale benchmarking and inspired several retrieval and
memory innovations described in this paper. Insights from
researchers and practitioners in the software engineering
and AI communities helped refine both methodology and
experimental design. Support from Kodezi’s investors enabled
the sustained research and development necessary to realize
Chronos. Continued engagement and rigorous testing from
the developer community have driven Chronos toward greater
reliability and practical impact.
References
[1] Brown, T. B., et al., ‘‘Language models are few-shot learners,’’
NeurIPS, 2020.
[2] Chen, M., et al., ‘‘Evaluating large language models trained on code,’’
arXiv:2107.03374, 2021.
[3] Austin, J., et al., ‘‘Program synthesis with large language models,’’
arXiv:2108.07732, 2021.
[4] Guo, D., et al., ‘‘GraphCodeBERT: Pre-training code representations
with data flow,’’ arXiv:2009.08366, 2021.
[5] Wang, Y., et al., ‘‘CodeT5: Identifier-aware unified pre-trained
encoder-decoder models for code understanding and generation,’’
arXiv:2109.00859, 2021.
[6] Tipirneni, S., Zhu, M., Reddy, C. K., ‘‘StructCoder: Structure-aware
transformer for code generation,’’ arXiv:2206.05239, 2023.
[7] Anthropic, ‘‘Claude 2 model card,’’ https://www.anthropic.com/
news/claude-2, 2023.
[8] Gao, T., et al., ‘‘Retrieval-Augmented Generation for Large Language
Models: A Survey,’’ arXiv:2308.07804, 2023.
[9] Allamanis, M., et al., ”Learning to represent programs with graphs,”
ICLR, 2018.
[10] Wei, Y., et al., ”Magicoder: Source Code Is All You Need,”
arXiv:2312.02120, 2023.
[11] Peng, S., et al., ”The Impact of AI on Developer Productivity: Evidence
from GitHub Copilot,” arXiv:2302.06590, 2023.
[12] Fried, D., et al., ”InCoder: A Generative Model for Code Infilling and
Synthesis,” ICLR, 2023.
[13] Ding, Y., et al., ”CrossCodeEval: A Diverse and Multilingual Benchmark for Cross-File Code Completion,” NeurIPS, 2023.
[14] Zhang, F., et al., ”RepoCoder: Repository-Level Code Completion
Through Iterative Retrieval and Generation,” EMNLP, 2023.
[15] Yang, J., et al., ”SWE-bench: Can Language Models Resolve RealWorld GitHub Issues?,” ICLR, 2024.
[16] Shrivastava, D., et al., ”Repository-Level Prompt Generation for Large
Language Models of Code,” ICML, 2023.
[17] Zhang, Y., et al., ”AutoCodeRover: Autonomous Program Improvement,” arXiv:2404.05427, 2024.
[18] Zhang, Q., et al., ”Enhancing Large Language Model Induced Code
Generation with Reinforcement Learning from Code Execution Feedback,” arXiv:2401.03374, 2024.
[19] Olausson, T., et al., ”Self-Repair: Teaching Language Models to Fix
Their Own Bugs,” arXiv:2302.04087, 2023.
[20] Lewis, P., et al., ”Retrieval-augmented generation for knowledgeintensive NLP tasks,” NeurIPS, 2020.
[21] Borgeaud, S., et al., ”Improving language models by retrieving from
trillions of tokens,” ICML, 2022.
[22] Izacard, G., et al., ”Atlas: Few-shot Learning with Retrieval Augmented
Language Models,” NeurIPS, 2022.
[23] Khandelwal, U., et al., ”Generalization through memorization: Nearest
neighbor language models,” ICLR, 2020.
[24] Lu, S., et al., ”ReACC: A Retrieval-Augmented Code Completion
Framework,” ACL, 2022.
[25] Nashid, N., et al., ”Retrieval-Based Prompt Selection for Code-Related
Few-Shot Learning,” ICSE, 2023.
[26] Hellendoorn, V., et al., ”Global relational models of source code,”
ICLR, 2020.
[27] Brody, S., et al., ”How Attentive are Graph Attention Networks?,”
ICLR, 2022.
[28] Velickovi ˇ c, P., et al., ”Graph attention networks,” ´ ICLR, 2018.
[29] Nijkamp, E., et al., ”CodeGen2: Lessons for Training LLMs on
Programming and Natural Languages,” arXiv:2305.02309, 2023.
[30] Roziere, B., et al., ”Code Llama: Open Foundation Models for Code,” `
arXiv:2308.12950, 2023.
[31] Li, R., et al., ”StarCoder: may the source be with you!,”
arXiv:2305.06161, 2023.
[32] Team, G., et al., ”CodeGemma: Open Code Models Based on Gemma,”
arXiv:2406.21146, 2024.
[33] Guo, D., et al., ”DeepSeek-Coder: When the Large Language Model
Meets Programming,” arXiv:2401.14196, 2024.
[34] Lozhkov, A., et al., ”StarCoder 2 and The Stack v2: The Next
Generation,” arXiv:2402.19173, 2024.
[35] Muennighoff, N., et al., ”OctoPack: Instruction Tuning Code Large
Language Models,” arXiv:2308.07124, 2023.
[36] Luo, Z., et al., ”WizardCoder: Empowering Code Large Language
Models with Evol-Instruct,” arXiv:2306.08568, 2023.
[37] Zheng, T., et al., ”OpenCodeInterpreter: Integrating Code Generation
with Execution and Refinement,” arXiv:2402.14658, 2024.
[38] Gao, L., et al., ”PAL: Program-aided Language Models,” ICML, 2023.
[39] Chen, X., et al., ”CodeT: Code Generation with Generated Tests,”
ICLR, 2023.
[40] Ni, A., et al., ”LEVER: Learning to Verify Language-to-Code
Generation with Execution,” ICML, 2023.
[41] Anysphere, ”Cursor: The AI Code Editor,” https://cursor.sh,
2024.
[42] OpenAI, ”OpenAI Codex,” https://openai.com/blog/
openai-codex, 2023.
[43] Google, ”Gemini Code Assist,” https://cloud.google.com/
gemini/docs/code-assist, 2024.
[44] Microsoft, ”GitHub Copilot Documentation,” https://docs.github.
com/copilot, 2023. Allamanis, M., Brockschmidt, M., Khademi, M.
‘‘Learning to represent programs with graphs,’’ arXiv:1711.00740,
2017.
[45] Arora, S., et al., ‘‘Context length extrapolation in large language
models,’’ arXiv:2307.03172, 2023.
[46] Feng, Z., et al., ‘‘CodeBERT: A Pre-Trained Model for Programming
and Natural Languages,’’ arXiv:2002.08155, 2020.
[47] OpenAI, ‘‘GPT-4 Technical Report,’’ arXiv:2303.08774, 2023.
[48] Jiang, N., et al., ‘‘SelfEvolve: A Code Evolution Framework via Large
Language Models,’’ arXiv:2306.02907, 2023.
[49] Chen, X., et al., ‘‘Teaching Large Language Models to Self-Debug,’’
ICLR, 2024.
[50] Madaan, A., et al., ‘‘Self-Refine: Iterative Refinement with SelfFeedback,’’ NeurIPS, 2023.
[51] Kodezi, ‘‘Kodezi Chronos: Autonomous https://kodezi.com/os,
2025.