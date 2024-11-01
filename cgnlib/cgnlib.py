import networkx as nx
import netcenlib as ncl
import matplotlib.pyplot as plt
import csv
from networkx.algorithms.community import girvan_newman

class cgnlib:
    def __init__(self, file, method="closeness"):
        self.file = file
        self.method = method
        self.best_communities = None
        self.GraphSet = self._create_graph_from(file)

    def _create_graph_from(self, file):
        G = nx.Graph()
        try:
            with open(file, 'r') as file:
                for line in file.readlines():
                    parts = line.strip().split(' ')
                    if len(parts) != 2:
                        raise ValueError("Each line must contain exactly two nodes separated by a space.")
                    source, target = parts
                    G.add_edge(source, target)
        except Exception as e:
            print(f"Error importing graph: {e}")
            print("Please ensure the input file is in the correct format with each line containing exactly two nodes separated by a space.")
            return None
        return G
    
    
    def coverage(self, graph, clusters):
        total_edges = graph.number_of_edges()
        intra_cluster_edges = sum(graph.subgraph(cluster).number_of_edges() for cluster in clusters)
        coverage = intra_cluster_edges / total_edges if total_edges > 0 else 0
        return coverage

    def _calculate_centrality_for_edges(self, G, metric='closeness'):
        edge_to_node = {edge: i for i, edge in enumerate(G.edges(), 1)}
        H = nx.Graph()

        for edge1 in G.edges():
            H.add_node(edge_to_node[edge1])
            for edge2 in G.edges():
                if edge1 != edge2 and len(set(edge1) & set(edge2)) > 0:
                    H.add_edge(edge_to_node[edge1], edge_to_node[edge2])

        centrality = None
        if metric == 'closeness':
            centrality = nx.closeness_centrality(H)
        elif metric == 'betweenness':
            centrality = nx.betweenness_centrality(H)
        elif metric == 'pagerank':
            centrality = nx.pagerank(H)
        elif metric == 'degree':
            centrality = dict(H.degree())
        elif hasattr(ncl.algorithms, f'{metric}_centrality'):
            centrality_func = getattr(ncl.algorithms, f'{metric}_centrality')
            centrality = centrality_func(H)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        centrality_edge_mapping = {edge: centrality[edge_to_node[edge]] for edge in G.edges()}
        return centrality_edge_mapping

    def detect_classic_gn(self):
        graph = self.GraphSet.copy()  # Copy of the original graph to work with
        comp = girvan_newman(graph)   # Run NetworkX's Girvan-Newman algorithm
        classic_communities = tuple(sorted(c) for c in next(comp))  # Get first partition of communities
        # Store or return results as needed
        self.best_communities = classic_communities 
        return classic_communities

    def detect_gn(self, method='closeness'):

        if method=='Girvan-Newman':
            return self.detect_classic_gn()

        graph = self.GraphSet.copy()
        best_modularity = -1
        best_communities = []
        while True:
            communities = list(nx.connected_components(graph))
            current_modularity = round(nx.community.modularity(self.GraphSet, communities), 4)

            if current_modularity >= best_modularity:
                best_modularity = current_modularity
                best_communities = communities

            if current_modularity < best_modularity:
                break

            edge_centrality = self._calculate_centrality_for_edges(graph, metric=method)
            max_centrality = max(edge_centrality.values())

            edges_with_max_centrality = [edge for edge, centrality in edge_centrality.items() if centrality == max_centrality]
            graph.remove_edges_from(edges_with_max_centrality)

        self.best_communities = best_communities
        return best_communities

    def evaluate_community_quality(self):
        if self.best_communities is None:
            return None

        communities = self.best_communities
        G = self.GraphSet

        modularity = nx.community.modularity(G, communities)

        conductances = []
        for community in communities:
            if len(community) == len(G.nodes):
                conductance = None
            else:
                conductance = nx.algorithms.cuts.conductance(G, community)
            conductances.append(conductance)

        # Filter out None values to calculate metrics
        valid_conductances = [c for c in conductances if c is not None]
        if valid_conductances:
            average_conductance = sum(valid_conductances) / len(valid_conductances)
            min_conductance = min(valid_conductances)
            max_conductance = max(valid_conductances)
        else:
            average_conductance = min_conductance = max_conductance = None

        # Calculate coverage
        coverage_metric = self.coverage(G, communities)

        # Add metrics to the dictionary
        metrics = {
            "Modularity": modularity,
            "Average Conductance": average_conductance,
            "Min Conductance": min_conductance,
            "Max Conductance": max_conductance,
            "Coverage": coverage_metric,
            "Conductance": conductances,
            "Number of Communities": len(communities)
        }
        return metrics


    def visualize_best_communities(self, save_path=None):
        if self.best_communities is None:
            print("No communities detected. Please run the detect_gn method first.")
            return

        pos = nx.spring_layout(self.GraphSet)
        colors = plt.get_cmap('tab10')

        for i, community in enumerate(self.best_communities):
            nx.draw_networkx_nodes(self.GraphSet, pos, nodelist=list(community), node_color=[colors(i)], label=f'Community {i}')
        nx.draw_networkx_edges(self.GraphSet, pos)
        nx.draw_networkx_labels(self.GraphSet, pos)

        plt.legend()
        if save_path:
            plt.savefig(save_path)
            print(f"Visualization saved as {save_path}")
            plt.close()  # Close the plot to prevent it from displaying
        else:
            plt.show()  # Only show the plot if not saving

    def visualize_with_node_attributes(self, attribute='degree', save_path=None):
        if self.best_communities is None:
            print("No communities detected. Please run the detect_gn method first.")
            return

        pos = nx.spring_layout(self.GraphSet)
        colors = plt.get_cmap('tab10')

        if attribute == 'degree':
            node_attr = dict(self.GraphSet.degree())
        elif hasattr(ncl.algorithms, f'{attribute}_centrality'):
            node_attr_func = getattr(ncl.algorithms, f'{attribute}_centrality')
            node_attr = node_attr_func(self.GraphSet)
        else:
            raise ValueError(f"Unsupported attribute: {attribute}")

        for i, community in enumerate(self.best_communities):
            node_sizes = [node_attr[node] * 100 for node in community]
            nx.draw_networkx_nodes(self.GraphSet, pos, nodelist=list(community), node_color=[colors(i)], node_size=node_sizes, label=f'Community {i}')
        nx.draw_networkx_edges(self.GraphSet, pos)
        nx.draw_networkx_labels(self.GraphSet, pos)

        plt.legend()
        if save_path:
            plt.savefig(save_path)
            print(f"Visualization saved as {save_path}")
            plt.close()  # Close the plot to prevent it from displaying
        else:
            plt.show()  # Only show the plot if not saving

    def save_communities_to_csv(self, filename='community_results.csv'):
        if self.best_communities is None:
            print("No communities detected. Please run the detect_gn method first.")
            return

        node_to_community = {}
        for label, community in enumerate(self.best_communities):
            for node in community:
                node_to_community[node] = label

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['NodeNumber', 'ClusterLabel'])
            for node, label in node_to_community.items():
                writer.writerow([node, label])
        print(f"Communities saved to {filename}")
        