# myprofile.py
import networkx as nx
import netcenlib as ncl
import matplotlib.pyplot as plt
import csv

class cgnlib:
    """
    A class for community detection in graphs using various centrality measures.

    This class provides methods for loading a graph, performing community detection using
    the Girvan-Newman algorithm, evaluating community quality, and visualizing results. 

    Attributes:
        file (str): The path to the graph file.
        method (str): The centrality measure to use for community detection.
        best_communities (list of set): The communities identified by the detection algorithm.
        GraphSet (networkx.Graph): The graph representation of the input data.
    """

    def __init__(self, file, method="closeness"):
        """
        Initializes the cgnlib class with the provided graph file and centrality method.

        Args:
            file (str): The path to the graph file.
            method (str): The centrality measure to use for community detection. Defaults to 'closeness'.
        """
        self.file = file
        self.method = method
        self.best_communities = None
        self.GraphSet = self._create_graph_from(file)

    def _create_graph_from(self, file):
        """
        Creates a graph from the input file.

        Args:
            file (str): The path to the graph file.

        Returns:
            networkx.Graph: A graph object representing the data from the file.

        Raises:
            ValueError: If any line in the file does not contain exactly two nodes.
        """
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

    def _calculate_centrality_for_edges(self, G, metric='closeness'):
        """
        Calculates centrality for edges in the graph based on the specified metric.

        Args:
            G (networkx.Graph): The graph for which centrality is to be calculated.
            metric (str): The centrality metric to use. Options include 'closeness', 'betweenness', 'pagerank', 'degree', 'bary'.

        Returns:
            dict: A mapping from edges to their centrality values.

        Raises:
            ValueError: If an unsupported metric is provided.
        """
        edge_to_node = {edge: i for i, edge in enumerate(G.edges(), 1)}
        H = nx.Graph()

        for edge1 in G.edges():
            H.add_node(edge_to_node[edge1])
            for edge2 in G.edges():
                if edge1 != edge2 and len(set(edge1) & set(edge2)) > 0:
                    H.add_edge(edge_to_node[edge1], edge_to_node[edge2])

        if metric == 'closeness':
            centrality = nx.closeness_centrality(H)
        elif metric == 'betweenness':
            centrality = nx.betweenness_centrality(H)
        elif metric == 'pagerank':
            centrality = nx.pagerank(H)
        elif metric == 'degree':
            centrality = dict(H.degree())
        elif metric == 'bary':
            centrality = ncl.barycenter_centrality(H)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        centrality_edge_mapping = {edge: centrality[edge_to_node[edge]] for edge in G.edges()}

        return centrality_edge_mapping

    def detect_gn(self, method='closeness'):
        """
        Performs community detection using the Girvan-Newman algorithm.

        Args:
            method (str): The centrality measure to use for detecting communities. Defaults to 'closeness'.

        Returns:
            list of set: A list of sets, where each set contains nodes in a detected community.
        """
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
        """
        Evaluates the quality of the detected communities.

        Returns:
            dict: A dictionary containing 'Modularity' and 'Average Conductance' metrics.
            - 'Modularity' (float): The modularity of the detected communities.
            - 'Average Conductance' (float): The average conductance of the detected communities.
            - 'Conductance' (list of float): List of conductance values for each community.
        """
        if self.best_communities is None:
            return None

        communities = self.best_communities
        G = self.GraphSet

        modularity = nx.community.modularity(G, communities)

        conductances = []
        for community in communities:
            # Check if the community is the entire graph
            if len(community) == len(G.nodes):
                conductance = None  # or define a specific value, e.g., 0 or float('inf')
            else:
                conductance = nx.algorithms.cuts.conductance(G, community)
            conductances.append(conductance)

        # Handle case when conductance is not computable
        valid_conductances = [c for c in conductances if c is not None]
        if valid_conductances:
            average_conductance = sum(valid_conductances) / len(valid_conductances)
        else:
            average_conductance = None  # or define a specific value

        metrics = {
            "Modularity": modularity,
            "Average Conductance": average_conductance,
            "Conductance": conductances,
        }

        return metrics

    def visualize_best_communities(self, save_path=None):
        """
        Visualizes the detected communities and optionally saves the visualization to a file.

        Args:
            save_path (str): The path to the file where the visualization should be saved. If None, the plot will be displayed but not saved.
        """
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
        plt.show()

    def visualize_with_node_attributes(self, attribute='degree', save_path=None):
        """
        Visualizes the graph with node sizes scaled by the specified attribute and optionally saves the visualization to a file.

        Args:
            attribute (str): The node attribute to visualize. Options include 'degree', 'closeness', 'betweenness', 'pagerank'.
            save_path (str): The path to the file where the visualization should be saved. If None, the plot will be displayed but not saved.
        
        Raises:
            ValueError: If an unsupported attribute is provided.
        """
        if self.best_communities is None:
            print("No communities detected. Please run the detect_gn method first.")
            return

        pos = nx.spring_layout(self.GraphSet)
        colors = plt.get_cmap('tab10')

        # Calculate the node attribute to visualize
        if attribute == 'degree':
            node_attr = dict(self.GraphSet.degree())
        elif attribute == 'closeness':
            node_attr = nx.closeness_centrality(self.GraphSet)
        elif attribute == 'betweenness':
            node_attr = nx.betweenness_centrality(self.GraphSet)
        elif attribute == 'pagerank':
            node_attr = nx.pagerank(self.GraphSet)
        else:
            raise ValueError(f"Unsupported attribute: {attribute}")

        for i, community in enumerate(self.best_communities):
            node_sizes = [node_attr[node] * 100 for node in community]  # Scale node sizes by attribute
            nx.draw_networkx_nodes(self.GraphSet, pos, nodelist=list(community), node_color=[colors(i)], node_size=node_sizes, label=f'Community {i}')
        nx.draw_networkx_edges(self.GraphSet, pos)
        nx.draw_networkx_labels(self.GraphSet, pos)

        plt.legend()
        if save_path:
            plt.savefig(save_path)
            print(f"Visualization saved as {save_path}")
        plt.show()

    def save_communities_to_csv(self, filename='community_results.csv'):
        """
        Saves the detected communities to a CSV file.

        Args:
            filename (str): The name of the file where the communities should be saved. Defaults to 'community_results.csv'.
        
        The CSV file will contain two columns: 'NodeNumber' and 'ClusterLabel'.
        """
        if self.best_communities is None:
            print("No communities detected. Please run the detect_gn method first.")
            return

        # Assign cluster labels to each node
        node_to_community = {}
        for label, community in enumerate(self.best_communities):
            for node in community:
                node_to_community[node] = label

        # Write to CSV
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['NodeNumber', 'ClusterLabel'])
            for node, label in node_to_community.items():
                writer.writerow([node, label])
        print(f"Communities saved to {filename}")

if __name__ == '__main__':
    cgn = cgnlib('soc.graph')
    best_communities = cgn.detect_gn(method='closeness')
    cgn.visualize_best_communities("best_communities.png")
    cgn.save_communities_to_csv('community_results.csv')
    print(cgn.evaluate_community_quality())
    cgn.visualize_with_node_attributes(attribute="closeness")
