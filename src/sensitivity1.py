import json
import matplotlib.pyplot as plt
from collections import defaultdict

def read_json(file_path):
    """
    Reads the JSON file and computes the maximum accuracy for each depth level.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            candidates = data.get("data", {}).get("candidates", [])
            depth_accuracy_map = defaultdict(list)

            # Group accuracies by depth
            for candidate in candidates:
                depth = candidate["depth"]
                # accuracy = candidate["predicted"]["accuracy"]
                accuracy = candidate["predicted"]["f1_score"]
                depth_accuracy_map[depth].append(accuracy)

            # Get max accuracy for each depth
            depths = sorted(depth_accuracy_map.keys())
            max_accuracies = [max(depth_accuracy_map[depth]) for depth in depths]
            return depths, max_accuracies
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return [], []

def plot_scatter():
    """
    Reads data from JSON files and plots a connected scatter plot.
    """
    # File paths
    included_file = "../example/api/model/included_tree.json"
    excluded_file = "../example/api/model/excluded_tree.json"
    all_trees_file = "../example/api/model/all_tree.json"

    # Read data
    included_depths, included_accuracies = read_json(included_file)
    excluded_depths, excluded_accuracies = read_json(excluded_file)
    all_depths, all_accuracies = read_json(all_trees_file)

    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Plot data with lines
    plt.plot(included_depths, included_accuracies, '-o', color='blue', label='Included Trees')
    plt.plot(excluded_depths, excluded_accuracies, '-o', color='red', label='Excluded Trees')
    plt.plot(all_depths, all_accuracies, '-o', color='green', label='All Trees')

    # Add labels, title, and legend
    plt.xlabel("Tree Depth")
    plt.ylabel("Max Accuracy")
    plt.title("Tree Depth vs. Max Accuracy")
    plt.legend()
    plt.grid(True)

    # Save or show plot
    plt.savefig("scatter_plot_connected.png")  # Save the plot as an image
    plt.show()  # Display the plot

# Execute the plot function
if __name__ == "__main__":
    plot_scatter()
