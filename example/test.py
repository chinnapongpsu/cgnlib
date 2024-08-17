from cgnlib import cgnexp

exp = cgnexp('hdy.graph')
exp.run_experiments(metrics=['closeness', 
    'betweenness', 
    'pagerank', 
    'degree', 
    'heatmap', 
    'harmonic', 
    'subgraph', 
    'laplacian',
    'rumor'], save_images=True)
exp.print_results()
exp.export_results_to_csv('experiment_results.csv')