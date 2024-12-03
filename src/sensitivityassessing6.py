import json
import matplotlib.pyplot as plt

# Load data from tree.json
with open("../example/api/model/trees.json", "r") as file:
    data = json.load(file)

# Extract candidates
candidates = data["data"]["candidates"]

# Prepare a dictionary to store the maximum accuracy for each depth
depth_accuracy = {}

# Iterate through candidates and update depth_accuracy dictionary
for candidate in candidates:
    depth = candidate["params"]["max_depth"]
    accuracy = candidate["predicted"]["accuracy"]
    if depth not in depth_accuracy:
        depth_accuracy[depth] = accuracy
    else:
        depth_accuracy[depth] = max(depth_accuracy[depth], accuracy)

# Sort depth-accuracy pairs by depth
sorted_depth_accuracy = sorted(depth_accuracy.items())

# Extract depths and accuracies for plotting
depths = [item[0] for item in sorted_depth_accuracy]
accuracies = [item[1] for item in sorted_depth_accuracy]

# Extract Pareto front data
pareto_depths = data["data"]["pareto_front"]["depth__f1_score"]

# Plotting
plt.figure(figsize=(10, 6))

# Plot maximum accuracy vs. depth
plt.plot(depths, accuracies, marker="o", label="Max Accuracy by Depth", color="blue")

# Highlight intersection with Pareto front
intersection_depths = [depth for depth in pareto_depths if depth in depths]
intersection_accuracies = [depth_accuracy[depth] for depth in intersection_depths]
plt.scatter(intersection_depths, intersection_accuracies, color="red", label="Pareto Intersection", zorder=5)

# Labels and legend
plt.title("Accuracy vs. Depth and Pareto Intersection")
plt.xlabel("Tree Depth")
plt.ylabel("Maximum Accuracy")
plt.xticks(depths)  # Show all depth values
plt.legend()
plt.grid(True)

# Save or show the plot
plt.savefig("accuracy_vs_depth.png")  # Save the plot as an image
plt.show()
