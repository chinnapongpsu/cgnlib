# myprofile.py
import networkx as nx
import netcenlib as ncl
import time

class cgnlib:
	
	def __init__(self,file,method="closeness"):
		#self.GraphSet =nx.Graph()
		self.file=file
		self.method=method
		self.best_communities=None

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

	def _calculate_centrality_for_edges(self, G, metric='closeness'):
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
	

if __name__ == '__main__':
	cgn = cgnlib('soc.graph')
	best_communities = cgn.detect_gn(method='closeness')
	print( cgn.evaluate_community_quality() )
	# help(my)


