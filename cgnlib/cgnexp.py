import csv
import os
from cgnlib import cgnlib

class cgnexp:
    """
    A class to conduct experiments on community detection using different centrality measures.
    Supports multiple datasets in a single experiment run.
    """
    
    def __init__(self, files):
        """
        Initializes the cgnexp class with one or multiple graph datasets.

        Args:
            files (list of str): List of paths to graph files.
        """
        self.files = files if isinstance(files, list) else [files]
        self.results = []

    def run_experiments(self, metrics=None, save_images=False, save_folder='images/'):
        """
        Runs community detection experiments for the specified centrality metrics on each dataset.

        Args:
            metrics (list of str): List of centrality metrics to be tested. Defaults to a set list if None.
            save_images (bool): If True, saves visualizations for each metric and dataset.
        """
        if metrics is None:
            metrics = ['closeness', 'betweenness', 'pagerank', 'degree', 'bary']
        
        if save_images:
            os.makedirs(save_folder, exist_ok=True)

        for file in self.files:
            graph_data = cgnlib(file)
            dataset_name = os.path.splitext(os.path.basename(file))[0]
            
            for metric in metrics:
                try:
                    print(f"Running experiment on {dataset_name} with {metric} centrality...")
                    communities = graph_data.detect_gn(method=metric)
                    quality_metrics = graph_data.evaluate_community_quality()
                    modularity = quality_metrics.get("Modularity")
                    average_conductance = quality_metrics.get("Average Conductance")
                    min_conductance = quality_metrics.get("Min Conductance")
                    max_conductance = quality_metrics.get("Max Conductance")
                    coverage = quality_metrics.get("Coverage")
                    num_communities = len(communities)
                    
                    self.results.append({
                        'Dataset': dataset_name,
                        'Centrality Metric': metric,
                        'Modularity': modularity,
                        'Average Conductance': average_conductance,
                        'Min Conductance': min_conductance,
                        'Max Conductance': max_conductance,
                        'Coverage': coverage,
                        'Number of Communities': num_communities
                    })

                    if save_images:
                        image_filename = os.path.join(save_folder, f"{dataset_name}_{metric}.png")
                        graph_data.visualize_best_communities(image_filename)
                        print(f"Image saved as {image_filename}")

                except ValueError as e:
                    print(f"Error: {e}. Skipping {metric} centrality for {dataset_name}.")

    def print_results(self):
        """
        Prints the results of the experiments for all datasets to the console.
        """
        for result in self.results:
            print(f"Dataset: {result['Dataset']}")
            print(f"Centrality Metric: {result['Centrality Metric']}")
            print(f"Modularity: {result['Modularity']}")
            print(f"Average Conductance: {result['Average Conductance']}")
            print(f"Min Conductance: {result['Min Conductance']}")
            print(f"Max Conductance: {result['Max Conductance']}")
            print(f"Coverage: {result['Coverage']}")
            print(f"Number of Communities: {result['Number of Communities']}")
            print()
    
    def export_results_to_csv(self, filename='experiment_results.csv'):
        """
        Exports the results of the experiments to a CSV file, with each dataset's results prefixed by its name.

        Args:
            filename (str): The name of the file to save the results to. Defaults to 'experiment_results.csv'.
        """
        with open(filename, mode='w', newline='') as file:
            fieldnames = ['Dataset', 'Centrality Metric', 'Modularity', 'Average Conductance',
                          'Min Conductance', 'Max Conductance', 'Coverage', 'Number of Communities']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        print(f"Results exported to {filename}")

if __name__ == '__main__':
    # Multiple datasets can be specified
    exp = cgnexp(['Les.txt', 'Zachary.txt'])
    exp.run_experiments(metrics=['Girvan-Newman', 'closeness', 'betweenness', 'load', 'subgraph', 'algebraic'], save_images=True, save_folder='result')
    exp.print_results()
    exp.export_results_to_csv('experiment_results_multiple.csv')
