// Global object to store filter conditions
let filterConditions = {};
let accuracyAttributes = ["Accuracy [F1 score]", "F1 Never married", "F1 Married", "F1 Divorced or Separated", "F1 Widowed"]

// Function to update or remove a filter condition
function updateYFilter(yAttr, yValue, yMin) {
    if (accuracyAttributes.includes(yAttr)) {
        yValue = parseFloat(yValue.toFixed(4)); // Round to 4 decimals
    } else {
        yValue = Math.ceil(yValue); // Convert to an integer
    }

    if (yValue > yMin) {
        // Update or add the filter condition
        filterConditions[yAttr] = {
            condition: (data) => {
                const attributeName = getAttributeName(yAttr);
                // Check if the attribute is nested in `predicted`
                if (data["predicted"] && attributeName in data["predicted"]) {
                    return data["predicted"][attributeName] >= yValue;
                }
                // Otherwise, assume it's at the top level
                return data[attributeName] >= yValue;
            },
            attribute: getAttributeName(yAttr),
            sign: '>=',
            value: yValue // Store the raw value
        };
    } else {
        // Remove the filter condition if it goes back to the minimum value
        delete filterConditions[yAttr];
    }

    // Update the summary display
    displayFilterSummary(innerSummaryPanel);
}

// Function to update or remove a filter condition
function updateXFilter(xAttr, xValue, xMax) {
    if (accuracyAttributes.includes(xAttr)) {
        xValue = parseFloat(xValue.toFixed(4)); // Round to 4 decimals
    } else {
        xValue = Math.floor(xValue); // Convert to an integer
    }

    if (xValue < xMax) {
        // Update or add the filter condition
        filterConditions[xAttr] = {
            condition: (data) => {
                const attributeName = getAttributeName(xAttr);
                // Check if the attribute is nested in `predicted`
                if (data["predicted"] && attributeName in data["predicted"]) {
                    return data["predicted"][attributeName] <= xValue;
                }
                // Otherwise, assume it's at the top level
                return data[attributeName] <= xValue;
            },
            attribute: getAttributeName(xAttr),
            sign: '<=',
            value: xValue
        };    
    } else {
        // Remove the filter condition if it goes back to the minimum value
        delete filterConditions[xAttr];
    }

    // Update the summary display
    displayFilterSummary(innerSummaryPanel);
}

function applyFilterConditions(data, filterConditions) {
    return data.filter(tree => {
        // Check if the tree satisfies all valid filter conditions
        return Object.entries(filterConditions).every(([key, filterObj]) => {
            //console.log('condition key: ', key, filterObj.attribute);
            if (filterObj.attribute in tree || (tree["predicted"] && filterObj.attribute in tree["predicted"])) {
                // Apply the condition if the key exists in the tree or tree.predicted
                //console.log('key: ', filterObj.attribute, tree)
                return filterObj.condition(tree);
            }
            // Skip the condition if the key does not exist
            return true;
        });
    });
}

function updatePointsOpacity() {
    d3.selectAll("circle[tree_id]")
        .style("opacity", d => 
            data.candidates.some(candidate => candidate.tree_id === d.tree_id) ? 1 : 0.2
        );
}