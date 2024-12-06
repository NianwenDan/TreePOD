function createDropdown() {
    // Dropdown lists in the treemap div
    const dropdownOptions = ["Accuracy [F1 score]", "Nr. of Leaves", "Nr. of Nodes", "Nr. of Used Attributes", "Depth"];
    // TODO: add the following: ["Avg. significant digits", "F1 Never married", "F1 Married", "F1 Divorced or Separated", "F1 Widowed"]

    // select dropdown and add options
    const xAxisDropdown = d3.select('#x-axis-select');
    const yAxisDropdown = d3.select('#y-axis-select')

    xAxisDropdown.selectAll("option")
                    .data(dropdownOptions)
                    .enter()
                    .append("option")
                    .text(d => d);
    yAxisDropdown.selectAll("option")
                    .data(dropdownOptions)
                    .enter()
                    .append("option")
                    .text(d => d);
}

function updateTreeMap(paretoCandidates) {
    // Clear all existing treemaps and placeholder
    d3.select("#treemap").selectAll(".tree-map-svg").remove();
    d3.select("#treemap").selectAll(".placeholder-glow").remove();

    const paretoTreemap = paretoCandidates.filter(d => d["number_of_nodes"]>1);
    console.log('paretoTreemap: ', paretoTreemap);
    paretoTreemap.forEach(d => {
    //paretoTreemap.slice(0, 8).forEach(d => {
        // Create a container <div> for each treemap with margin
        const treemapContainer = d3.select("#treemap").append("div")
                                    .attr("class", "col col-md-auto me-2 tree-map-svg"); // bootstrap grid
            //.style("margin-top", "10px")
            //.style("margin-right", "10px");  // Add space between treemaps
            //.style("display", "inline-block");
    
        // Call createTreeMap and pass the container div as a parameter
        createTreeMap(d.tree_id, treemapContainer);
    });
}

function createTreeMap(id, treemapContainer) {
    // Dimensions for the treemap
    const element = treemapContainer.node().getBoundingClientRect();
    const width = element.width * 0.9;
    const height = element.height * 0.9;

    // Extract the hierarchy data
    const rootData = hierarchy.find(entry => entry.tree_id === id)['hierarchy_data'];

    // Create a root hierarchy
    const root = d3.hierarchy(rootData).sum(d => d.value);

    // Create the treemap layout
    d3.treemap()
        .size([width, height])
        .padding(1)(root);

    // Append an SVG to the treemap div
    const treemap = treemapContainer
        .append("svg").attr("tree_id", id)
        .attr("width", width)
        .attr("height", height);

    // Add rectangles for each node
    const nodes = treemap.selectAll("g")
        .data(root.leaves())
        .enter()
        .append("g")
        .attr("transform", d => `translate(${d.x0}, ${d.y0})`);

    // Add rectangles
    nodes.append("rect")
        .attr("class", "leaf")
        .attr("width", d => d.x1 - d.x0)
        .attr("height", d => d.y1 - d.y0)
        .attr("fill", "white"); // Background color for the leaf

    // Add quasi-random pixel representation for class distribution
    nodes.append("foreignObject")
        .attr("width", d => d.x1 - d.x0)
        .attr("height", d => d.y1 - d.y0)
        .append("xhtml:div")
        .style("width", d => `${d.x1 - d.x0}px`)
        .style("height", d => `${d.y1 - d.y0}px`)
        .style("display", "grid")
        .style("grid-template-columns", "repeat(auto-fill, 2px)")
        .style("grid-auto-rows", "2px")
        .selectAll("div")
        .data(d => {
            // Get class distribution and scale to pixel count
            const pixelCount = Math.floor((d.x1 - d.x0) * (d.y1 - d.y0) / 4); // 2x2 px per pixel
            const distribution = d.data.classDistribution || {};
            const classPixels = Object.entries(distribution).flatMap(([className, freq]) => {
                const count = Math.round(freq * pixelCount);
                return Array(count).fill(className);
            });
            return d3.shuffle(classPixels); // Shuffle for quasi-random placement
        })
        .enter()
        .append("div")
        .style("width", "2px")
        .style("height", "2px")
        .style("background-color", className => {
            switch (className) {
                case "Married": return "#002f6c";
                case "Never married": return "#ebbe4d";
                case "Divorced or Separated": return "#cd1c18";
                case "Widowed": return "#00965f";
                case "Not Fraud": return "#002f6c";
                case "Fraud": return "#ebbe4d";
                default: return "gray";
            }
        });
}

// When a Pareto-optimal tree is selected in the scatter plot, the corresponding treemap will be highlighted.
function highlightTreeMap(treeId) {
    d3.selectAll("svg[tree_id]").style("border", "none");
    if (treeId) {
        d3.select(`svg[tree_id='${treeId}']`).style("border", "3px solid black").style('padding', '2px');
    }
}

function attachTreeMapClickListener() {
    d3.selectAll("svg[tree_id]").on("click", function (event) {
        //console.log('Click this treemap: ', this);
        const treeId = d3.select(this).attr("tree_id");
        highlightTreeMap(treeId);
        selectedTreeId = treeId;
        highlightScatterPoint(treeId);
        displayDecisionTree();
    });
}