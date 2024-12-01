// Assuming that you have the JSON data loaded in as "data"
// and the JSON file is called "tree_candidates.json"
let paretoFront = null;
let paretoCandidates = null;
let paretoFrontTreeNum = 0;
let xAttribute = "Nr. of Nodes";
let yAttribute = "Accuracy [F1 score]";
let all_data = null;
let data, hierarchy;

Promise.all([
    d3.json("http://127.0.0.1:5500/api/v1/model/trees"),
    d3.json("http://127.0.0.1:5500/api/v1/tree/hierarchy")
    //d3.json("http://127.0.0.1:5500/example/api/model/trees.json"),
    //d3.json("http://127.0.0.1:5500/example/api/tree/hierarchy_data.json")
])
.then(([json1, json2]) => {
    data = json1.data;
    hierarchy = json2.data;
    all_data = JSON.parse(JSON.stringify(json1.data));
    //console.log("Data 1:", data);
    //console.log("Data 2:", hierarchy);
    initializeApplication();
})
.catch(error => {
    console.error("Error loading JSON files:", error);
});

//d3.json("http://127.0.0.1:5500/example/api/model/trees.json").then(function(response) {
// Store the original data before applying any filter
//const data = response.data;
//all_data = JSON.parse(JSON.stringify(response.data));

function initializeApplication() {
    // Execute this step to get the initial pareto optimal tree number and display in the summary panel
    updateParetoFront(data, "Nr. of Nodes", "Accuracy [F1 score]");

    createSummaryPanel(data);

    // Dropdown list for x and y axis of the scatter plot will be placed next to the treemaps. See treeMaps.js
    createDropdown();


    const margin = {top: 60, right: 20, bottom: 40, left: 80};//{top: 20, right: 20, bottom: 40, left: 60};

    const scatterPlotDiv = d3.select("#scatter-plot-svg");
    const scatterPlotWidth = parseInt(scatterPlotDiv.style("width")) - margin.left - margin.right;
    const scatterPlotHeight = parseInt(scatterPlotDiv.style("height")) - margin.top - margin.bottom;
    console.log(scatterPlotWidth, scatterPlotHeight)
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
    updateScatterPlot("Nr. of Nodes", "Accuracy [F1 score]");
    updateTreeMap(paretoCandidates);

    // Add event listeners to dropdowns
    d3.select("#x-axis-select").on("change", function() {
        xAttribute = d3.select("#x-axis-select").property("value");
        updateParetoFront(data, xAttribute, yAttribute);
        updateSummaryPanel();
        updateScatterPlot(xAttribute, yAttribute);
        updateTreeMap(paretoCandidates);
    });

    d3.select("#y-axis-select").on("change", function() {
        yAttribute = d3.select("#y-axis-select").property("value");
        updateParetoFront(data, xAttribute, yAttribute);
        updateSummaryPanel();
        updateScatterPlot(xAttribute, yAttribute);
        updateTreeMap(paretoCandidates);
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
            .domain([0, d3.max(xValues) * 1.05])
            .range([0, scatterPlotWidth * 0.9]); // Downsize the plot to fit within the svg

        const yScale = d3.scaleLinear()
            .domain([d3.min(yValues), d3.max(yValues) + (d3.max(yValues) - d3.min(yValues)) * 0.05])
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
        enableFilter(); 
        
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

        function enableFilter() {
            // Add a grey area to indicate the filter range
            const xFilterArea = svg.append("rect")
                .attr("x", scatterPlotWidth - margin.right * 2.5) // Initial position
                .attr("y", 0) // Align with the draggable rectangle
                .attr("width", 0) // Initially no area is highlighted
                .attr("height", scatterPlotHeight - margin.bottom) // Same height as the filter rectangle
                .attr("fill", "grey")
                .attr("opacity", 0.5); // Semi-transparent

            // Add drag behavior for X-axis filter rectangle
            const xDrag = d3.drag()
                .on("drag", function (event) {
                    const x = Math.min(scatterPlotWidth * 0.9, Math.max(0, event.x));
                    d3.select(this).attr("x", x);
                    
                    // Update the grey filter area based on the current position of the rectangle
                    const rectX = parseFloat(d3.select(this).attr("x")); // Current x position of the rectangle
                    const initialX = scatterPlotWidth * 0.9; // Initial x position of the rectangle
                    const greyWidth = rectX - initialX; // Calculate the grey area width
                    xFilterArea.attr("x", greyWidth >= 0 ? initialX : rectX) // Ensure it covers left-to-right motion
                        .attr("width", Math.abs(greyWidth)); // Use absolute value for width
                    
                    // Call the update function with the new filter value
                    updateXFilter(xAttr, xScale.invert(x), xScale.domain()[1]);
                    data.candidates = [...applyFilterConditions(all_data.candidates, filterConditions)];
                    console.log("Filtered Trees:", data.candidates.length, all_data.candidates.length);
                });

            // Add X-axis filter rectangle
            const xFilterRect = svg.append("rect")
                .attr("x", scatterPlotWidth * 0.9)
                .attr("y", scatterPlotHeight/2-margin.bottom)
                .attr("width", 10)
                .attr("height", 40)
                .attr("stroke", "black")
                //.attr("stroke-width", 1.5)
                .attr("fill", "white")
                .call(xDrag);

            // Add a grey area to indicate the filter range for the y-axis
            const yFilterArea = svg.append("rect")
                .attr("x", 0) // Align with the y-axis
                .attr("y", scatterPlotHeight - margin.bottom - 8) // Initial position
                .attr("width", scatterPlotWidth * 0.9) // Full width
                .attr("height", 0) // Initially no area is highlighted
                .attr("fill", "grey")
                .attr("opacity", 0.5); // Semi-transparent

            // Add drag behavior for Y-axis filter rectangle
            const yDrag = d3.drag()
            .on("drag", function (event) {
                // Constrain the rectangle to only move upwards
                const initialY = scatterPlotHeight - margin.bottom; // Initial position of the rectangle
                const y = Math.min(initialY, Math.max(0, event.y)); // Ensure `y` does not exceed `initialY`
        
                // Update the position of the rectangle
                d3.select(this).attr("y", y);
        
                // Update the grey filter area based on the current position of the rectangle
                const rectY = parseFloat(d3.select(this).attr("y")); // Current y position of the rectangle
                const greyHeight = initialY - rectY; // Calculate the grey area height
                yFilterArea.attr("y", rectY).attr("height", greyHeight); // Update the height of the grey area
        
                // Call the update function with the new filter value
                updateYFilter(yAttr, yScale.invert(y), yScale.domain()[0]);
                data.candidates = [...applyFilterConditions(all_data.candidates, filterConditions)];
                console.log("Filtered Trees:", data.candidates.length, all_data.candidates.length);
            });        

            // Add Y-axis filter rectangle
            const yFilterRect = svg.append("rect")
                .attr("x", (scatterPlotWidth - margin.left) / 2)
                .attr("y", scatterPlotHeight - margin.bottom-8) // Initial position
                .attr("width", 40) // Rectangle width
                .attr("height", 10) // Rectangle height
                .attr("stroke", "black")
                .attr("fill", "white")
                .call(yDrag);
        }
    }
}

// Each time the x and y attributes are selected from the dropdown list, retrieve the pareto front tree ids from json
function updateParetoFront(data, xAttr, yAttr) {
        // Pareto-front
        const sortedParetoKey = [getAttributeName(xAttr), getAttributeName(yAttr)].sort().join('__');
        console.log('data: ', data);
        paretoFront = data.pareto_front[sortedParetoKey];
        paretoFrontTreeNum = paretoFront.length;
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