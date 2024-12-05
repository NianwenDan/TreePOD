import json

def include_trees(input_json_path, output_json_path, included_features):
    """
    Filters trees to include only those with specific features in their feature subset.
    """
    try:
        with open(input_json_path, 'r') as file:
            data = json.load(file)

        # Filter trees that include at least one of the specified features
        included_candidates = [
            candidate for candidate in data["data"]["candidates"]
            if any(feature in included_features for feature in candidate["feature_subset"])
        ]

        # Update the JSON structure
        data["data"]["candidates"] = included_candidates
        data["data"]["total_candidates_after_pruning"] = len(included_candidates)

        with open(output_json_path, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"Included data saved to {output_json_path}. Total trees included: {len(included_candidates)}")
    except Exception as e:
        print(f"An error occurred in include_trees: {e}")


def exclude_trees(input_json_path, output_json_path, excluded_features):
    """
    Filters trees to exclude those with specific features in their feature subset.
    """
    try:
        with open(input_json_path, 'r') as file:
            data = json.load(file)

        # Filter trees that do NOT include any of the excluded features
        filtered_candidates = [
            candidate for candidate in data["data"]["candidates"]
            if not any(feature in excluded_features for feature in candidate["feature_subset"])
        ]

        # Update the JSON structure
        data["data"]["candidates"] = filtered_candidates
        data["data"]["total_candidates_after_pruning"] = len(filtered_candidates)

        with open(output_json_path, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"Excluded data saved to {output_json_path}. Total trees after exclusion: {len(filtered_candidates)}")
    except Exception as e:
        print(f"An error occurred in exclude_trees: {e}")


def include_all_trees(input_json_path, output_json_path):
    """
    Includes all tree IDs without filtering.
    """
    try:
        with open(input_json_path, 'r') as file:
            data = json.load(file)

        # Simply update the count and write all candidates to output
        data["data"]["total_candidates_after_pruning"] = len(data["data"]["candidates"])

        with open(output_json_path, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"All tree data saved to {output_json_path}. Total trees included: {len(data['data']['candidates'])}")
    except Exception as e:
        print(f"An error occurred in include_all_trees: {e}")


# Example usage
if __name__ == "__main__":
    input_json = "../example/api/model/trees.json"  # Input file path
    output_json_include = "../example/api/model/included_tree.json"  # Output for included trees
    output_json_exclude = "../example/api/model/excluded_tree.json"  # Output for excluded trees
    output_json_all = "../example/api/model/all_tree.json"  # Output for all trees

    # Define features to include or exclude (can be passed dynamically from frontend)
    features_to_include = ["income", "capital-gain"]  # Example for inclusion
    features_to_exclude = ["income", "capital-loss"]  # Example for exclusion

    # Run each function
    include_trees(input_json, output_json_include, features_to_include)
    exclude_trees(input_json, output_json_exclude, features_to_exclude)
    include_all_trees(input_json, output_json_all)

