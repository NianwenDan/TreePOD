// Assuming that you have the JSON data loaded in as "data"
// and the JSON file is called "tree_candidates.json"
let paretoFront = null;
let paretoCandidates = null;

d3.json("trees.5.json").then(function(data) {

    createSummaryPanel(data);

    // Dropdown list for x and y axis of the scatter plot will be placed next to the treemaps. See treeMaps.js
    createDropdown();

    const margin = {top: 20, right: 20, bottom: 40, left: 60};
    const scatterPlotDiv = d3.select("#scatter-plot");
    const scatterPlotWidth = parseInt(scatterPlotDiv.style("width")) - margin.left - margin.right;
    const scatterPlotHeight = parseInt(scatterPlotDiv.style("height")) - margin.top - margin.bottom;

    // Create SVG for the Scatter Plot in the scatter-plot div
    scatterPlotDiv.selectAll("svg").remove(); // Clear previous plot if it exists
    const svg = scatterPlotDiv.append("svg")
        .attr("width", scatterPlotWidth + margin.left + margin.right)
        .attr("height", scatterPlotHeight + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // Initial plot update
    d3.select("#x-axis-select").property("value", "Nr. of Nodes");
    d3.select("#y-axis-select").property("value", "Accuracy [F1 score]");
    updateParetoFront(data, "Nr. of Nodes", "Accuracy [F1 score]");
    updateScatterPlot("Nr. of Nodes", "Accuracy [F1 score]");

    // Add event listeners to dropdowns
    d3.select("#x-axis-select").on("change", function() {
        const xAttribute = d3.select("#x-axis-select").property("value");
        const yAttribute = d3.select("#y-axis-select").property("value");
        updateParetoFront(data, xAttribute, yAttribute);
        updateScatterPlot(xAttribute, yAttribute);
    });

    d3.select("#y-axis-select").on("change", function() {
        const xAttribute = d3.select("#x-axis-select").property("value");
        const yAttribute = d3.select("#y-axis-select").property("value");
        updateParetoFront(data, xAttribute, yAttribute);
        updateScatterPlot(xAttribute, yAttribute);
    });

    function updateScatterPlot(xAttr, yAttr) {
        // Clear previous plot
        scatterPlotDiv.selectAll("svg").remove();
        const svg = scatterPlotDiv.append("svg")
            .attr("width", scatterPlotWidth + margin.left + margin.right)
            .attr("height", scatterPlotHeight + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left}, ${margin.top})`);

        // Prepare data
        const candidates = data.candidates;
        const xValues = candidates.map(d => getAttributeValue(d, xAttr));
        const yValues = candidates.map(d => getAttributeValue(d, yAttr));

        // Define the scales
        const xScale = d3.scaleLinear()
            .domain([0, d3.max(xValues)])
            .range([0, scatterPlotWidth * 0.9]); // Downsize the plot to fit within the svg

        const yScale = d3.scaleLinear()
            .domain([d3.min(yValues), d3.max(yValues)])
            .range([scatterPlotHeight * 0.9, 0]); // Downsize the plot to fit within the svg

        // Axes
        svg.selectAll(".axis").remove();
        const xAxis = d3.axisBottom(xScale);
        const yAxis = d3.axisLeft(yScale);

        svg.append("g")
            .attr("class", "axis x-axis")
            .attr("transform", `translate(0, ${scatterPlotHeight * 0.9})`)
            .call(xAxis)
            .append('text')
            .attr('fill', '#000')
            .attr('x', scatterPlotWidth / 2)
            .attr('y', 40)
            .attr('text-anchor', 'middle')
            .style('font-size', '12px')
            .style('font-family', 'Arial')
            .text(xAttr);

        svg.append("g")
            .attr("class", "axis y-axis")
            .call(yAxis);

        svg.append('text')
            .attr('fill', '#000')
            .attr('transform', 'rotate(-90)')
            .attr('x', -scatterPlotHeight / 2)
            .attr('y', -40)
            .attr('text-anchor', 'middle')
            .style('font-size', '12px')
            .style('font-family', 'Arial')
            .text(yAttr);

        // Bind data and create scatter plot points
        const points = svg.selectAll("circle").data(candidates);
        points.enter()
            .append("circle")
            .merge(points)
            .attr("cx", d => xScale(getAttributeValue(d, xAttr)))
            .attr("cy", d => yScale(getAttributeValue(d, yAttr)))
            .attr("r", d => paretoFront.includes(d.tree_id) ? 4 : 2) // Increase point size for Pareto-optimal candidates
            .style("fill", "black");
        points.exit().remove();
        
        drawParetoFront(svg, xAttr, yAttr);
        updateTreeMap(paretoCandidates);       
        
        // Draw line connecting Pareto-optimal points
        function drawParetoFront(svg, xAttr, yAttr) {
            const line = d3.line()
                .x(d => xScale(getAttributeValue(d, xAttr)))
                .y(d => yScale(getAttributeValue(d, yAttr)))
                .curve(d3.curveMonotoneX); // Smooth line
            
            svg.append("path")
                .datum(paretoCandidates)
                .attr("fill", "none")
                .attr("stroke", '#69b3a2')
                .attr("stroke-width", 2)
                .attr("d", line);
        }
    }
});

// Each time the x and y attributes are selected from the dropdown list, retrieve the pareto front tree ids from json
function updateParetoFront(data, xAttr, yAttr) {
        // Pareto-front
        const sortedParetoKey = [getAttributeName(xAttr), getAttributeName(yAttr)].sort().join('_');
        paretoFront = data.pareto_front[sortedParetoKey];
        console.log('key: ', sortedParetoKey);
        console.log('pareto_front: ', paretoFront);

        // Pareto-optimal points
        paretoCandidates = data.candidates.filter(d => paretoFront.includes(d.tree_id));
        paretoCandidates.sort((a, b) => getAttributeValue(a, xAttr) - getAttributeValue(b, xAttr));  
}

// Helper function to get the attribute value from the candidate data
function getAttributeValue(d, attribute) {
    switch (attribute) {
        case "Accuracy [F1 score]":
            return d["predicted"]["f1_score"];
        case "Nr. of Leaves":
            return d["number_of_leaves"] || 0; // Assuming "max_leaf_nodes" is available in params
        case "Nr. of Nodes":
            return d["number_of_nodes"];
        case "Nr. of Used Attributes":
            return d["number_of_used_attributes"];
        case "Depth":
            return d["depth"];
        default:
            return 0;
    }
}

// Helper function to map the attribute name from the dropdown list to the json attribute name
function getAttributeName(attribute) {
    switch (attribute) {
        case "Accuracy [F1 score]":
            return "f1_score";
        case "Nr. of Leaves":
            return "number_of_leaves"; // Assuming "max_leaf_nodes" is available in params
        case "Nr. of Nodes":
            return "number_of_nodes";
        case "Nr. of Used Attributes":
            return "number_of_used_attributes"; //Object.keys(d.params.attributes).length;
        case "Depth":
            return "depth";
        default:
            return 0;
    }
}    