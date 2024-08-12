# myprofile.py
import networkx as nx
from cdlib import evaluation
from cdlib import NodeClustering
import time

class Cgnlib:
	'''
	Example:


	'''
	def __init__(self,file,method="closeness"):
		self.GraphSet =nx.Graph()
		self.file=file
		self.method=method
  
		# Declaring private method

	def _calculate_closeness_centrality_for_edges(self,G):
		edge_to_node = {edge: i for i, edge in enumerate(G.edges(), 1)}
		H = nx.Graph()
		for edge1 in G.edges():
			H.add_node(edge_to_node[edge1])
			for edge2 in G.edges():
				if edge1 != edge2 and len(set(edge1) & set(edge2)) > 0:
					H.add_edge(edge_to_node[edge1], edge_to_node[edge2])
		closeness_centrality = nx.closeness_centrality(H)
		closeness_centrality_edge_mapping = {edge: closeness_centrality[edge_to_node[edge]] for edge in G.edges()}
		return closeness_centrality_edge_mapping
	def _community_detection_edges_centrality(self):
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
			edge_closeness = self._calculate_closeness_centrality_for_edges(graph)

			max_closeness = max(edge_closeness.values())
			edges_with_max_closeness = [edge for edge, closeness in edge_closeness.items() if closeness == max_closeness]
			graph.remove_edges_from(edges_with_max_closeness)

		return best_communities

	def detect(self):
		with open(self.file, 'r') as self.file:
			for line in self.file.readlines()[0:]:
				source, target = line.strip().split(' ')
				self.GraphSet.add_edge(source, target)
		start_time = time.time()
		if self.method == 'closeness':
			result = self._community_detection_edges_centrality()
		elif self.method == 'betweenness':
			result= nx.edge_betweenness_centrality(self.GraphSet)
		else:
			raise ValueError("Unsupported centrality method. Choose 'closeness' or 'betweenness'.")

		for i, community in enumerate(result):
			print(f"Community {i + 1}: Nodes = {community}")
		print(f"Modularity (G): {nx.community.modularity(self.GraphSet, result)}")
		communities = [list(s) for s in result]
		coms = NodeClustering(communities, graph=None, method_name="Closeness")
		modularity=evaluation.newman_girvan_modularity(self.GraphSet, coms)
		conductance=evaluation.conductance(self.GraphSet, coms)
		print(f"Modularity with CDLIB: {evaluation.newman_girvan_modularity(self.GraphSet, coms)}")
		print(f"Conductance: {evaluation.conductance(self.GraphSet, coms)}")
		end_time = time.time()
		execution_time = end_time - start_time
		print(f"Execution time: {execution_time} seconds")
		return {"communities":communities,"modularity":modularity,"conductance":conductance}

		# # Create graph self.GraphSet from self.file
		# file = 'filename'
		# # self.GraphSet = create_graph_from(file)
		# G = nx.karate_club_graph()

		# Perform community detection on G
		


if __name__ == '__main__':
	cgn = Cgnlib('example/soc.graph',"closeness")
	cgn.detect()
	# help(my)


