#!/usr/bin/env python3
"""
Retrieval-Specific Benchmarks for Kodezi Chronos 2025
Tests AGR performance against various retrieval strategies
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
import networkx as nx
import random
import time

@dataclass
class RetrievalQuery:
    """Represents a retrieval query for debugging"""
    query_id: str
    query_text: str
    error_type: str
    seed_nodes: List[str]
    relevant_nodes: Set[str]
    complexity: int  # k-hop depth required
    
@dataclass
class CodeGraph:
    """Represents a code repository as a graph"""
    graph: nx.DiGraph
    node_types: Dict[str, str]
    edge_types: Dict[Tuple[str, str], str]
    embeddings: Dict[str, np.ndarray]
    
class RetrievalBenchmarkGenerator:
    """Generates retrieval-specific benchmarks"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_code_graph(self, 
                          n_nodes: int = 10000,
                          avg_degree: int = 10) -> CodeGraph:
        """
        Generate a synthetic code graph for testing
        
        Args:
            n_nodes: Number of nodes (files/functions)
            avg_degree: Average node degree
            
        Returns:
            CodeGraph object
        """
        # Create base graph with scale-free properties (realistic for code)
        G = nx.barabasi_albert_graph(n_nodes, avg_degree // 2)
        G = G.to_directed()
        
        # Assign node types
        node_types = {}
        type_distribution = {
            'function': 0.4,
            'class': 0.2,
            'file': 0.15,
            'test': 0.1,
            'config': 0.05,
            'documentation': 0.05,
            'log_point': 0.05
        }
        
        for node in G.nodes():
            node_type = np.random.choice(
                list(type_distribution.keys()),
                p=list(type_distribution.values())
            )
            node_types[node] = node_type
        
        # Assign edge types based on node types
        edge_types = {}
        for u, v in G.edges():
            u_type = node_types[u]
            v_type = node_types[v]
            
            # Realistic edge type assignment
            if u_type == 'function' and v_type == 'function':
                edge_type = np.random.choice(['calls', 'references'], p=[0.7, 0.3])
            elif u_type == 'class' and v_type == 'class':
                edge_type = np.random.choice(['inherits', 'uses'], p=[0.3, 0.7])
            elif u_type == 'test' and v_type in ['function', 'class']:
                edge_type = 'tests'
            elif u_type == 'file' and v_type == 'file':
                edge_type = 'imports'
            elif v_type == 'log_point':
                edge_type = 'logs'
            else:
                edge_type = 'references'
            
            edge_types[(u, v)] = edge_type
        
        # Generate embeddings (768-dim as mentioned in paper)
        embeddings = {}
        for node in G.nodes():
            # Create embeddings that cluster by node type
            base_embedding = np.random.randn(768) * 0.1
            
            # Add type-specific bias
            type_idx = list(type_distribution.keys()).index(node_types[node])
            base_embedding[type_idx * 100:(type_idx + 1) * 100] += 0.5
            
            embeddings[node] = base_embedding / np.linalg.norm(base_embedding)
        
        return CodeGraph(G, node_types, edge_types, embeddings)
    
    def generate_retrieval_queries(self,
                                 code_graph: CodeGraph,
                                 n_queries: int = 1000) -> List[RetrievalQuery]:
        """
        Generate retrieval queries with known ground truth
        
        Args:
            code_graph: The code graph to query
            n_queries: Number of queries to generate
            
        Returns:
            List of RetrievalQuery objects
        """
        queries = []
        
        for i in range(n_queries):
            # Select query complexity (k-hop depth)
            complexity = np.random.choice([1, 2, 3, 4, 5], p=[0.2, 0.3, 0.3, 0.15, 0.05])
            
            # Select seed nodes
            n_seeds = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
            seed_nodes = random.sample(list(code_graph.graph.nodes()), n_seeds)
            
            # Find relevant nodes within k-hops
            relevant_nodes = set()
            for seed in seed_nodes:
                # BFS to find k-hop neighbors
                current_level = {seed}
                for hop in range(complexity):
                    next_level = set()
                    for node in current_level:
                        next_level.update(code_graph.graph.successors(node))
                        next_level.update(code_graph.graph.predecessors(node))
                    current_level = next_level
                    relevant_nodes.update(current_level)
            
            # Generate query text based on bug type
            error_type = random.choice([
                'NullPointerException',
                'IndexOutOfBounds',
                'TypeError',
                'RaceCondition',
                'MemoryLeak',
                'PerformanceRegression'
            ])
            
            query_text = self._generate_query_text(error_type, seed_nodes, code_graph)
            
            queries.append(RetrievalQuery(
                query_id=f"query_{i:04d}",
                query_text=query_text,
                error_type=error_type,
                seed_nodes=[str(n) for n in seed_nodes],
                relevant_nodes={str(n) for n in relevant_nodes},
                complexity=complexity
            ))
        
        return queries
    
    def _generate_query_text(self, 
                           error_type: str, 
                           seed_nodes: List[int],
                           code_graph: CodeGraph) -> str:
        """Generate realistic query text"""
        templates = {
            'NullPointerException': "{error} in {location} when calling {method}",
            'IndexOutOfBounds': "Array index out of bounds at {location} index {index}",
            'TypeError': "Type mismatch in {location}: expected {expected}, got {actual}",
            'RaceCondition': "Data race detected between {location1} and {location2}",
            'MemoryLeak': "Memory leak detected in {location}, {size}MB not freed",
            'PerformanceRegression': "Performance degraded by {percent}% in {location}"
        }
        
        template = templates.get(error_type, "Error in {location}")
        
        # Fill template with synthetic data
        location = f"node_{seed_nodes[0]}"
        return template.format(
            error=error_type,
            location=location,
            method=f"method_{random.randint(1, 100)}",
            index=random.randint(0, 1000),
            expected="String",
            actual="Integer",
            location1=f"node_{seed_nodes[0]}",
            location2=f"node_{seed_nodes[-1] if len(seed_nodes) > 1 else seed_nodes[0] + 1}",
            size=random.randint(10, 1000),
            percent=random.randint(50, 500)
        )

class RetrievalStrategies:
    """Implements various retrieval strategies for comparison"""
    
    @staticmethod
    def flat_top_k_retrieval(query: RetrievalQuery,
                            code_graph: CodeGraph,
                            k: int = 50) -> Set[str]:
        """Traditional flat top-k retrieval based on embedding similarity"""
        # Get query embedding (average of seed node embeddings)
        query_embedding = np.mean([
            code_graph.embeddings[int(seed)] 
            for seed in query.seed_nodes
        ], axis=0)
        
        # Calculate similarities
        similarities = []
        for node, embedding in code_graph.embeddings.items():
            sim = np.dot(query_embedding, embedding)
            similarities.append((node, sim))
        
        # Sort and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return {str(node) for node, _ in similarities[:k]}
    
    @staticmethod
    def bm25_retrieval(query: RetrievalQuery,
                      code_graph: CodeGraph,
                      k: int = 50) -> Set[str]:
        """BM25-based retrieval (simulated)"""
        # Simplified BM25 simulation
        # In practice, would use actual text content
        relevant_types = {
            'NullPointerException': ['function', 'class'],
            'TypeError': ['function', 'class', 'test'],
            'RaceCondition': ['function', 'log_point'],
            'MemoryLeak': ['function', 'class'],
            'PerformanceRegression': ['function', 'config']
        }
        
        preferred_types = relevant_types.get(query.error_type, ['function'])
        
        # Score nodes based on type preference and proximity to seeds
        scores = {}
        G = code_graph.graph
        
        for node in G.nodes():
            score = 0.0
            
            # Type bonus
            if code_graph.node_types[node] in preferred_types:
                score += 0.5
            
            # Proximity bonus
            for seed in query.seed_nodes:
                try:
                    distance = nx.shortest_path_length(G, int(seed), node)
                    score += 1.0 / (1 + distance)
                except nx.NetworkXNoPath:
                    pass
            
            scores[node] = score
        
        # Return top-k
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return {str(node) for node, _ in sorted_nodes[:k]}
    
    @staticmethod
    def graph_rag_retrieval(query: RetrievalQuery,
                           code_graph: CodeGraph,
                           k: int = 50) -> Set[str]:
        """Static graph-based retrieval"""
        # Start from seed nodes and expand based on edge weights
        G = code_graph.graph
        retrieved = set()
        
        # Priority queue for expansion
        from heapq import heappush, heappop
        queue = []
        
        for seed in query.seed_nodes:
            heappush(queue, (0, int(seed)))
        
        visited = set()
        
        while queue and len(retrieved) < k:
            score, node = heappop(queue)
            
            if node in visited:
                continue
            
            visited.add(node)
            retrieved.add(str(node))
            
            # Expand neighbors with static weights
            for neighbor in list(G.successors(node)) + list(G.predecessors(node)):
                if neighbor not in visited:
                    # Simple static weight
                    edge_weight = 0.8 if code_graph.node_types[neighbor] == 'function' else 0.5
                    heappush(queue, (score + (1 - edge_weight), neighbor))
        
        return retrieved
    
    @staticmethod
    def chronos_agr_retrieval(query: RetrievalQuery,
                            code_graph: CodeGraph,
                            confidence_threshold: float = 0.89) -> Tuple[Set[str], Dict]:
        """
        Chronos AGR retrieval with adaptive expansion
        
        Returns:
            Tuple of (retrieved_nodes, metadata)
        """
        G = code_graph.graph
        retrieved = set()
        visited = set()
        
        # Initialize with seed nodes
        seeds = [int(s) for s in query.seed_nodes]
        current_nodes = set(seeds)
        k = 1
        
        metadata = {
            'iterations': [],
            'confidence_progression': [],
            'nodes_per_hop': []
        }
        
        # Edge type weights from paper
        edge_weights = {
            'stack_trace': 0.97,
            'tests': 0.95,
            'logs': 0.92,
            'imports': 0.90,
            'calls': 0.85,
            'inherits': 0.80,
            'references': 0.60
        }
        
        while True:
            # Get k-hop neighbors
            next_nodes = set()
            for node in current_nodes:
                # Get neighbors with weighted scoring
                for neighbor in list(G.successors(node)) + list(G.predecessors(node)):
                    if neighbor not in visited:
                        # Calculate score based on edge type
                        edge_type = code_graph.edge_types.get((node, neighbor), 'references')
                        weight = edge_weights.get(edge_type, 0.5)
                        
                        # Semantic similarity
                        node_emb = code_graph.embeddings[node]
                        neighbor_emb = code_graph.embeddings[neighbor]
                        semantic_sim = np.dot(node_emb, neighbor_emb)
                        
                        # Combined score
                        score = weight * 0.7 + semantic_sim * 0.3
                        
                        if score > 0.5:  # Threshold for inclusion
                            next_nodes.add(neighbor)
            
            # Update retrieved and visited
            retrieved.update(str(n) for n in next_nodes)
            visited.update(next_nodes)
            
            # Calculate confidence (simplified)
            confidence = min(len(retrieved) / (10 * k), 0.95)
            
            # Track metadata
            metadata['iterations'].append({
                'k': k,
                'new_nodes': len(next_nodes),
                'total_retrieved': len(retrieved),
                'confidence': confidence
            })
            metadata['confidence_progression'].append(confidence)
            metadata['nodes_per_hop'].append(len(retrieved))
            
            # Check termination conditions
            if confidence >= confidence_threshold or k >= 5 or len(next_nodes) == 0:
                break
            
            # Adaptive expansion
            current_nodes = next_nodes
            k += 1
        
        metadata['final_k'] = k
        metadata['total_nodes'] = len(retrieved)
        
        return retrieved, metadata

class RetrievalBenchmarkEvaluator:
    """Evaluates retrieval strategies on benchmarks"""
    
    def __init__(self):
        self.strategies = {
            'flat_top_k': RetrievalStrategies.flat_top_k_retrieval,
            'bm25': RetrievalStrategies.bm25_retrieval,
            'graph_rag': RetrievalStrategies.graph_rag_retrieval,
            'chronos_agr': RetrievalStrategies.chronos_agr_retrieval
        }
    
    def evaluate_all_strategies(self,
                              queries: List[RetrievalQuery],
                              code_graph: CodeGraph) -> Dict:
        """Evaluate all retrieval strategies"""
        results = {}
        
        for strategy_name, strategy_func in self.strategies.items():
            print(f"\nEvaluating {strategy_name}...")
            results[strategy_name] = self.evaluate_strategy(
                strategy_func, queries, code_graph
            )
        
        return results
    
    def evaluate_strategy(self,
                         strategy_func,
                         queries: List[RetrievalQuery],
                         code_graph: CodeGraph) -> Dict:
        """Evaluate a single retrieval strategy"""
        metrics = {
            'precision_at_k': {k: [] for k in [10, 20, 50]},
            'recall_at_k': {k: [] for k in [10, 20, 50]},
            'f1_at_k': {k: [] for k in [10, 20, 50]},
            'retrieval_times': [],
            'nodes_retrieved': [],
            'complexity_analysis': {i: {'precision': [], 'recall': []} 
                                  for i in range(1, 6)}
        }
        
        for query in queries:
            start_time = time.time()
            
            # Execute retrieval
            if 'agr' in strategy_func.__name__:
                retrieved, metadata = strategy_func(query, code_graph)
            else:
                retrieved = strategy_func(query, code_graph)
                metadata = {}
            
            retrieval_time = time.time() - start_time
            
            # Calculate metrics
            relevant = query.relevant_nodes
            
            for k in [10, 20, 50]:
                retrieved_k = list(retrieved)[:k]
                precision = len(set(retrieved_k) & relevant) / k if k > 0 else 0
                recall = len(set(retrieved_k) & relevant) / len(relevant) if relevant else 0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                
                metrics['precision_at_k'][k].append(precision)
                metrics['recall_at_k'][k].append(recall)
                metrics['f1_at_k'][k].append(f1)
            
            metrics['retrieval_times'].append(retrieval_time)
            metrics['nodes_retrieved'].append(len(retrieved))
            
            # Complexity-specific analysis
            complexity = query.complexity
            if complexity in metrics['complexity_analysis']:
                p = len(retrieved & relevant) / len(retrieved) if retrieved else 0
                r = len(retrieved & relevant) / len(relevant) if relevant else 0
                metrics['complexity_analysis'][complexity]['precision'].append(p)
                metrics['complexity_analysis'][complexity]['recall'].append(r)
        
        # Aggregate results
        aggregated = {
            'avg_precision_at_k': {
                k: np.mean(values) for k, values in metrics['precision_at_k'].items()
            },
            'avg_recall_at_k': {
                k: np.mean(values) for k, values in metrics['recall_at_k'].items()
            },
            'avg_f1_at_k': {
                k: np.mean(values) for k, values in metrics['f1_at_k'].items()
            },
            'avg_retrieval_time': np.mean(metrics['retrieval_times']),
            'avg_nodes_retrieved': np.mean(metrics['nodes_retrieved']),
            'complexity_performance': {
                complexity: {
                    'avg_precision': np.mean(data['precision']),
                    'avg_recall': np.mean(data['recall'])
                }
                for complexity, data in metrics['complexity_analysis'].items()
                if data['precision']
            }
        }
        
        return aggregated

class ComplexityVerification:
    """Verify O(k log d) complexity claim for AGR"""
    
    @staticmethod
    def verify_agr_complexity(code_graphs: List[CodeGraph],
                            query_sets: List[List[RetrievalQuery]]) -> Dict:
        """
        Verify AGR complexity across different graph sizes
        
        Args:
            code_graphs: Graphs of different sizes
            query_sets: Corresponding query sets
            
        Returns:
            Complexity analysis results
        """
        results = {
            'graph_sizes': [],
            'avg_degrees': [],
            'retrieval_times': [],
            'nodes_retrieved': [],
            'k_values': []
        }
        
        for graph, queries in zip(code_graphs, query_sets):
            # Calculate graph statistics
            n_nodes = graph.graph.number_of_nodes()
            n_edges = graph.graph.number_of_edges()
            avg_degree = n_edges / n_nodes
            
            results['graph_sizes'].append(n_nodes)
            results['avg_degrees'].append(avg_degree)
            
            # Sample queries for timing
            sample_queries = random.sample(queries, min(100, len(queries)))
            
            times = []
            nodes = []
            k_vals = []
            
            for query in sample_queries:
                start = time.time()
                retrieved, metadata = RetrievalStrategies.chronos_agr_retrieval(
                    query, graph
                )
                elapsed = time.time() - start
                
                times.append(elapsed)
                nodes.append(len(retrieved))
                k_vals.append(metadata.get('final_k', 1))
            
            results['retrieval_times'].append(np.mean(times))
            results['nodes_retrieved'].append(np.mean(nodes))
            results['k_values'].append(np.mean(k_vals))
        
        # Fit to O(k log d) model
        k_vals = np.array(results['k_values'])
        d_vals = np.array(results['avg_degrees'])
        expected_complexity = k_vals * np.log(d_vals)
        
        # Calculate correlation
        actual_times = np.array(results['retrieval_times'])
        correlation = np.corrcoef(expected_complexity, actual_times)[0, 1]
        
        results['complexity_verification'] = {
            'correlation': correlation,
            'fits_model': correlation > 0.8,
            'expected_complexity': expected_complexity.tolist(),
            'actual_times': actual_times.tolist()
        }
        
        return results


if __name__ == "__main__":
    # Generate test data
    print("Generating code graph...")
    generator = RetrievalBenchmarkGenerator()
    code_graph = generator.generate_code_graph(n_nodes=10000, avg_degree=10)
    
    print(f"Generated graph with {code_graph.graph.number_of_nodes()} nodes "
          f"and {code_graph.graph.number_of_edges()} edges")
    
    # Generate queries
    print("\nGenerating retrieval queries...")
    queries = generator.generate_retrieval_queries(code_graph, n_queries=1000)
    print(f"Generated {len(queries)} queries")
    
    # Evaluate strategies
    print("\nEvaluating retrieval strategies...")
    evaluator = RetrievalBenchmarkEvaluator()
    results = evaluator.evaluate_all_strategies(queries[:100], code_graph)  # Sample for speed
    
    # Print results
    print("\n" + "="*60)
    print("RETRIEVAL BENCHMARK RESULTS")
    print("="*60)
    
    for strategy, metrics in results.items():
        print(f"\n{strategy.upper()}:")
        print(f"  Precision@10: {metrics['avg_precision_at_k'][10]:.3f}")
        print(f"  Recall@10: {metrics['avg_recall_at_k'][10]:.3f}")
        print(f"  F1@10: {metrics['avg_f1_at_k'][10]:.3f}")
        print(f"  Avg retrieval time: {metrics['avg_retrieval_time']:.3f}s")
        print(f"  Avg nodes retrieved: {metrics['avg_nodes_retrieved']:.1f}")
    
    # Verify complexity
    print("\n" + "="*60)
    print("COMPLEXITY VERIFICATION")
    print("="*60)
    
    # Generate graphs of different sizes
    graph_sizes = [1000, 5000, 10000, 50000]
    graphs = []
    query_sets = []
    
    for size in graph_sizes:
        print(f"Generating graph with {size} nodes...")
        g = generator.generate_code_graph(n_nodes=size, avg_degree=10)
        q = generator.generate_retrieval_queries(g, n_queries=100)
        graphs.append(g)
        query_sets.append(q)
    
    complexity_results = ComplexityVerification.verify_agr_complexity(graphs, query_sets)
    
    print(f"\nComplexity verification:")
    print(f"  Correlation with O(k log d): {complexity_results['complexity_verification']['correlation']:.3f}")
    print(f"  Fits model: {complexity_results['complexity_verification']['fits_model']}")