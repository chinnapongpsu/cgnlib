# myprofile.py
import networkx as nx
from cdlib import evaluation
from cdlib import NodeClustering
import time

class Cgnlib:
	'''
	Example:


	'''
	def __init__(self,name):


		def calculate_closeness_centrality_for_edges(G):
			# Create a mapping from edge to node
			edge_to_node = {edge: i for i, edge in enumerate(G.edges(), 1)}
			# print("Edge to Node Mapping:", edge_to_node)

			# Create graph H
			H = nx.Graph()

			# Add all nodes in H according to edge_to_node
			for edge1 in G.edges():
				H.add_node(edge_to_node[edge1])
				for edge2 in G.edges():
					if edge1 != edge2 and len(set(edge1) & set(edge2)) > 0:
						H.add_edge(edge_to_node[edge1], edge_to_node[edge2])

			# Calculate closeness centrality in H
			closeness_centrality = nx.closeness_centrality(H)
			# print("Closeness Centrality in H:", closeness_centrality)

			# Create a mapping of closeness centrality from node to edge
			closeness_centrality_edge_mapping = {edge: closeness_centrality[edge_to_node[edge]] for edge in G.edges()}
			# print("Closeness Centrality Mapping from Edge to Node:", closeness_centrality_edge_mapping)

			return closeness_centrality_edge_mapping


		def community_detection_edges_centrality(G):
			graph = G.copy()
			best_modularity = -1
			best_communities = []
			while True:
				communities = list(nx.connected_components(graph))
				current_modularity = round(nx.community.modularity(G, communities), 4)
				if current_modularity >= best_modularity:
					best_modularity = current_modularity
					best_communities = communities

				if current_modularity < best_modularity:
					break
				edge_closeness = calculate_closeness_centrality_for_edges(graph)

				max_closeness = max(edge_closeness.values())
				edges_with_max_closeness = [edge for edge, closeness in edge_closeness.items() if closeness == max_closeness]
				graph.remove_edges_from(edges_with_max_closeness)

			return best_communities

		def create_graph_from(file):
			G = nx.Graph()
			with open(file, 'r') as file:
				for line in file.readlines()[0:]:
					source, target = line.strip().split(' ')
					G.add_edge(source, target)
			return G

		# Create graph G from file
		file = 'filename'
		# G = create_graph_from(file)
		G = nx.karate_club_graph()

		# Perform community detection on G
		start_time = time.time()
		result = community_detection_edges_centrality(G)
		for i, community in enumerate(result):
			print(f"Community {i + 1}: Nodes = {community}")
		print(f"Modularity (G): {nx.community.modularity(G, result)}")
		communities = [list(s) for s in result]
		coms = NodeClustering(communities, graph=None, method_name="Closeness")
		print(f"Modularity with CDLIB: {evaluation.newman_girvan_modularity(G, coms)}")
		print(f"Conductance: {evaluation.conductance(G, coms)}")
		end_time = time.time()
		execution_time = end_time - start_time
		print(f"Execution time: {execution_time} seconds")


if __name__ == '__main__':
	my = Cgnlib()
	
	# help(my)


