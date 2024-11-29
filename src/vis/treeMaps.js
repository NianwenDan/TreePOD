function updateTreeMap(paretoCandidates) {
    //paretoCandidates.slice(0, 8).forEach(d => createTreeMap(d));
    const paretoTreemap = paretoCandidates.filter(d => d["number_of_nodes"]>1);
    //console.log('paretoCandidates: ', paretoTreemap.slice(0, 8))
    paretoTreemap.slice(0, 8).forEach(d => {
        // Create a container <div> for each treemap with margin
        const treemapContainer = d3.select("#treemap").append("div")
            .style("margin-right", "10px")  // Add space between treemaps
            .style("display", "inline-block");  // Optional: to customize alignment
    
        // Call createTreeMap and pass the container div as a parameter
        createTreeMap(d, treemapContainer);
    });
}

function createTreeMap(d, treemapContainer) {
    //const filteredTree = candidates.find(candidate => candidate.tree_id === idx);

    // Dimensions for the treemap
    const width = 80;
    const height = 80;

    // Extract the hierarchy data
    const rootData = d.hierarchy_data;

    // Create a root hierarchy
    const root = d3.hierarchy(rootData).sum(d => d.value);

    // Create the treemap layout
    d3.treemap()
        .size([width, height])
        .padding(1)(root);

    // Append an SVG to the treemap div
    const treemap = treemapContainer//d3.select("#treemap")
        .append("svg")
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
                default: return "gray";
            }
        });
}