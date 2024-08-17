import csv
from cgnlib import cgnlib

class cgnexp:
    """
    A class to conduct experiments on community detection using different centrality measures.
    
    This class acts as a wrapper for the `cgnlib` class, providing functionality to load 
    a graph dataset, run community detection experiments using various centrality metrics, 
    and report the results.

    Attributes:
        file (str): The path to the graph file.
        graph_data (cgnlib): An instance of the `cgnlib` class to handle graph operations.
        results (list of dict): A list of dictionaries storing the results of the experiments.
    """
    
    def __init__(self, file):
        """
        Initializes the cgnexp class with the graph dataset.

        Args:
            file (str): The path to the graph file.
        """
        self.file = file
        self.graph_data = cgnlib(file)
        self.results = []
    
    def run_experiments(self, save_images=False):
        """
        Runs community detection experiments for all defined centrality metrics.

        This method executes the `detect_gn` method from the `cgnlib` class for each centrality 
        measure and collects modularity and average conductance metrics. Optionally saves 
        visualizations of the best communities.

        Args:
            save_images (bool): If True, saves visualizations of the best communities 
                                for each centrality metric. Default is False.
        
        Metrics tested:
            - 'closeness'
            - 'betweenness'
            - 'pagerank'
            - 'degree'
            - 'bary'
        """
        metrics = ['closeness', 'betweenness', 'pagerank', 'degree', 'bary']
        
        for metric in metrics:
            print(f"Running experiment with {metric} centrality...")
            self.graph_data.detect_gn(method=metric)
            quality_metrics = self.graph_data.evaluate_community_quality()
            modularity = quality_metrics.get("Modularity")
            average_conductance = quality_metrics.get("Average Conductance")
            
            self.results.append({
                'Centrality Metric': metric,
                'Modularity': modularity,
                'Average Conductance': average_conductance
            })
            
            if save_images:
                image_filename = f"{self.file.split('.')[0]}_{metric}.png"
                self.graph_data.visualize_best_communities(image_filename)
                print(f"Image saved as {image_filename}")
    
    def print_results(self):
        """
        Prints the results of the experiments to the console.

        The results include centrality metrics, modularity, and average conductance for each
        centrality measure tested.
        """
        for result in self.results:
            print(f"Centrality Metric: {result['Centrality Metric']}")
            print(f"Modularity: {result['Modularity']}")
            print(f"Average Conductance: {result['Average Conductance']}")
            print()
    
    def export_results_to_csv(self, filename='experiment_results.csv'):
        """
        Exports the results of the experiments to a CSV file.

        Args:
            filename (str): The name of the file to save the results to. Defaults to 'experiment_results.csv'.
        
        The CSV file will contain columns for 'Centrality Metric', 'Modularity', and 'Average Conductance'.
        """
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Centrality Metric', 'Modularity', 'Average Conductance'])
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        print(f"Results exported to {filename}")

if __name__ == '__main__':
    exp = cgnexp('hdy.graph')
    exp.run_experiments(save_images=True)
    exp.print_results()
    exp.export_results_to_csv('experiment_results.csv')
