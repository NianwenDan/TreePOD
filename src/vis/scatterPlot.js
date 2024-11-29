// Assuming that you have the JSON data loaded in as "data"
// and the JSON file is called "tree_candidates.json"

d3.json("trees.5.json").then(function(data) {
    const margin = {top: 20, right: 20, bottom: 40, left: 60};
    const scatterPlotDiv = d3.select("#scatter-plot");
    const scatterPlotWidth = parseInt(scatterPlotDiv.style("width")) - margin.left - margin.right;
    const scatterPlotHeight = parseInt(scatterPlotDiv.style("height")) - margin.top - margin.bottom;

    // Create the container for displaying rows in the summary panel
    const summaryPanel = d3.select("#summary-panel");
    const innerSummaryPanel = summaryPanel.append("div")
        .attr("class", "inner-summary-panel")
        .style("margin", "20px")
        .style("padding", "10px");

    // Row 1: Display Total Candidates before Pruning
    innerSummaryPanel.append("div").attr("class", "row").style("padding", "10px").style("border-bottom", "1px solid black").html(`<strong>${data.total_candidates_before_pruning} tree candidates generated</strong>`);
    innerSummaryPanel.append("br");

    // Placeholder Rows 2 - 3 with bottom border
    innerSummaryPanel.append("div").attr("class", "row").style("padding", "10px").style("border-bottom", "1px solid black").html(`<strong>Generation Parameter Filters (${data.total_candidates_before_pruning} trees)</strong>`);
    innerSummaryPanel.append("br");
    innerSummaryPanel.append("div").attr("class", "row").style("padding", "10px").style("border-bottom", "1px solid black").html(`<strong>Result Metric Filters (after filtering)</strong>`);
    innerSummaryPanel.append("br");

    // Last row without bottom border
    innerSummaryPanel.append("div").attr("class", "row").style("padding", "10px").html(`<strong>Pareto optimal: Number of trees</strong>`);
    innerSummaryPanel.append("br");

    // Create SVG for the Scatter Plot in the scatter-plot div
    scatterPlotDiv.selectAll("svg").remove(); // Clear previous plot if it exists
    const svg = scatterPlotDiv.append("svg")
        .attr("width", scatterPlotWidth + margin.left + margin.right)
        .attr("height", scatterPlotHeight + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // Dropdown lists in the treemap div
    const dropdownOptions = ["Accuracy [F1 score]", "Nr. of Leaves", "Nr. of Nodes", "Nr. of Used Attributes", "Depth"];

    const treemap = d3.select("#treemap");

    // Ensure dropdowns are appended to the div and not the SVG
    const dropdownContainer = treemap.append("div").attr("class", "dropdown-container");

    dropdownContainer.append("label").text("X Axis: ")
        .append("select")
        .attr("id", "x-axis-select")
        .selectAll("option")
        .data(dropdownOptions)
        .enter()
        .append("option")
        .text(d => d);

    // Initial plot update
    d3.select("#x-axis-select").property("value", "Nr. of Nodes");
    d3.select("#y-axis-select").property("value", "Accuracy [F1 score]");
    updateScatterPlot("Nr. of Nodes", "Accuracy [F1 score]");

    // Add event listeners to dropdowns
    d3.select("#x-axis-select").on("change", function() {
        const xAttribute = d3.select("#x-axis-select").property("value");
        const yAttribute = d3.select("#y-axis-select").property("value");
        updateScatterPlot(xAttribute, yAttribute);
    });

    d3.select("#y-axis-select").on("change", function() {
        const xAttribute = d3.select("#x-axis-select").property("value");
        const yAttribute = d3.select("#y-axis-select").property("value");
        updateScatterPlot(xAttribute, yAttribute);
    });

    dropdownContainer.append("label").text("Y Axis: ")
        .append("select")
        .attr("id", "y-axis-select")
        .selectAll("option")
        .data(dropdownOptions)
        .enter()
        .append("option")
        .text(d => d);

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
            .text(xAttr);

        svg.append("g")
            .attr("class", "axis y-axis")
            .call(yAxis);
            //.attr('fill', '#000')
            //.attr('transform', 'rotate(-90)')
            //.attr('x', -scatterPlotHeight / 2)
            //.attr('y', -40)
            //.attr('text-anchor', 'middle')
            //.style('font-size', '12px')
            //.text(yAttr);

        // Bind data and create scatter plot points
        const points = svg.selectAll("circle").data(candidates);

        // Pareto-front
        const sortedParetoKey = [getAttributeName(xAttr), getAttributeName(yAttr)].sort().join('_');
        const paretoFront = data.pareto_front[sortedParetoKey];
        //const paretoFront = data.pareto_front[`${xAttr}_${yAttr}`];
        console.log('key: ', sortedParetoKey);
        console.log('pareto_front: ', paretoFront);
        points.enter()
            .append("circle")
            .merge(points)
            .attr("cx", d => xScale(getAttributeValue(d, xAttr)))
            .attr("cy", d => yScale(getAttributeValue(d, yAttr)))
            //.attr("r", d => d.pareto_optimal ? 6 : 3) // Increase point size for Pareto-optimal candidates
            .attr("r", d => paretoFront.includes(d.tree_id) ? 4 : 2) // 
            .style("fill", "black");

        points.exit().remove();

        // Draw line connecting Pareto-optimal points
        const paretoCandidates = candidates.filter(d => paretoFront.includes(d.tree_id));
        paretoCandidates.sort((a, b) => getAttributeValue(a, xAttr) - getAttributeValue(b, xAttr));

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
        
        updateTreeMap(paretoCandidates);        
    }
});

// Helper function to get the attribute value from the candidate data
function getAttributeValue(d, attribute) {
    switch (attribute) {
        case "Accuracy [F1 score]":
            return d["predicted"]["f1_score"];
        case "Nr. of Leaves":
            return d.params.max_leaf_nodes || 0; // Assuming "max_leaf_nodes" is available in params
        case "Nr. of Nodes":
            return d["number_of_nodes"];
        case "Nr. of Used Attributes":
            return Object.keys(d.params.attributes).length;
        case "Depth":
            return d.params.max_depth || 0;
        default:
            return 0;
    }
}

// Helper function to get the attribute value from the candidate data
function getAttributeName(attribute) {
    switch (attribute) {
        case "Accuracy [F1 score]":
            return "f1_score";
        //case "Nr. of Leaves":
        //    return d.params.max_leaf_nodes || 0; // Assuming "max_leaf_nodes" is available in params
        case "Nr. of Nodes":
            return "number_of_nodes";
        //case "Nr. of Used Attributes":
        //    return Object.keys(d.params.attributes).length;
        //case "Depth":
        //    return d.params.max_depth || 0;
        default:
            return 0;
    }
}    