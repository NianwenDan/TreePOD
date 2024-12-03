// function renderConfusionMatrix(dataUrl, containerId) {
//     const width = 400;
//     const height = 400;
//     const margin = { top: 50, right: 50, bottom: 50, left: 50 };
//     const cellSize = 50;
//     const colors = ['yellow', 'blue', 'red', 'green'];

//     const svg = d3.select(containerId)
//         // .append("svg")
//         .attr("width", width + margin.left + margin.right)
//         .attr("height", height + margin.top + margin.bottom)
//         .append("g")
//         .attr("transform", `translate(${margin.left},${margin.top})`);

//     fetch(dataUrl)
//         .then(response => response.json())
//         .then(jsonData => {
//             const matrix = jsonData.data.confusion_matrix;
//             const labels = jsonData.data.labels;

//             const numRows = matrix.length;
//             const numCols = matrix[0].length;

//             const matrixWidth = numCols * cellSize;
//             const matrixHeight = numRows * cellSize;

//             // Draw cells
//             svg.selectAll(".cell")
//                 .data(matrix.flat().map((value, index) => {
//                     const row = Math.floor(index / numCols);
//                     const col = index % numCols;
//                     return { value, row, col };
//                 }))
//                 .enter()
//                 .append("rect")
//                 .attr("class", "cell")
//                 .attr("x", d => d.col * cellSize)
//                 .attr("y", d => d.row * cellSize)
//                 .attr("width", cellSize)
//                 .attr("height", cellSize)
//                 .style("fill", d => d3.interpolateBlues(d.value / d3.max(matrix.flat())))
//                 .style("stroke", "#000");

//             // Add cell values
//             svg.selectAll(".cell-text")
//                 .data(matrix.flat().map((value, index) => {
//                     const row = Math.floor(index / numCols);
//                     const col = index % numCols;
//                     return { value, row, col };
//                 }))
//                 .enter()
//                 .append("text")
//                 .attr("class", "cell-text")
//                 .attr("x", d => d.col * cellSize + cellSize / 2)
//                 .attr("y", d => d.row * cellSize + cellSize / 2)
//                 .attr("dy", ".35em")
//                 .attr("text-anchor", "middle")
//                 .text(d => d.value);

//             // Add predicted class color labels on top
//             svg.selectAll(".predicted-color")
//                 .data(labels)
//                 .enter()
//                 .append("line")
//                 .attr("class", "predicted-color")
//                 .attr("x1", (_, i) => i * cellSize)
//                 .attr("x2", (_, i) => (i + 1) * cellSize)
//                 .attr("y1", -10)
//                 .attr("y2", -10)
//                 .attr("stroke", (_, i) => colors[i % colors.length])
//                 .attr("stroke-width", 10);

//             // Add true class color labels on left
//             svg.selectAll(".true-color")
//                 .data(labels)
//                 .enter()
//                 .append("line")
//                 .attr("class", "true-color")
//                 .attr("x1", -10)
//                 .attr("x2", -10)
//                 .attr("y1", (_, i) => i * cellSize)
//                 .attr("y2", (_, i) => (i + 1) * cellSize)
//                 .attr("stroke", (_, i) => colors[i % colors.length])
//                 .attr("stroke-width", 10);

//             // Add axis labels
//             svg.append("text")
//                 .attr("class", "axis-label")
//                 .attr("x", matrixWidth / 2)
//                 .attr("y", -20)
//                 .attr("text-anchor", "middle")
//                 .text("Predicted Class");

//             svg.append("text")
//                 .attr("class", "axis-label")
//                 .attr("x", -50)
//                 .attr("y", matrixHeight / 2 + 30)
//                 .attr("text-anchor", "middle")
//                 .attr("transform", `rotate(-90, -50, ${matrixHeight / 2})`)
//                 .text("True Class");
//         })
//         .catch(error => console.error('Error loading JSON:', error));
// }

// // Call the function
// // renderConfusionMatrix('http://127.0.0.1:5500/api/v1/tree/confusion-matrix?treeId=1', "#confusion-matrix-svg");
// // renderConfusionMatrix('/example/api/tree/confusion-matrix.json', "#confusion-matrix-svg");

function renderConfusionMatrix(dataUrl, containerId) {
    const width = 400;
    const height = 400;
    const margin = { top: 50, right: 50, bottom: 50, left: 50 };
    const cellSize = 50;

    // Define the custom color mapping for classes
    const classColors = {
        "Married": "#002F6C",
        "Never married": "#EBBE4D",
        "Divorced or Separated": "#CD1C18",
        "Widowed": "#00965F"
    };

    const defaultColor = "gray"; // Fallback color if a label doesn't match

    const svg = d3.select(containerId)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    fetch(dataUrl)
        .then(response => response.json())
        .then(jsonData => {
            const matrix = jsonData.data.confusion_matrix;
            const labels = jsonData.data.labels;

            const numRows = matrix.length;
            const numCols = matrix[0].length;

            const matrixWidth = numCols * cellSize;
            const matrixHeight = numRows * cellSize;

            // Draw heatmap cells
            svg.selectAll(".cell")
                .data(matrix.flat().map((value, index) => {
                    const row = Math.floor(index / numCols);
                    const col = index % numCols;
                    return { value, row, col };
                }))
                .enter()
                .append("rect")
                .attr("class", "cell")
                .attr("x", d => d.col * cellSize)
                .attr("y", d => d.row * cellSize)
                .attr("width", cellSize)
                .attr("height", cellSize)
                .style("fill", d => {
                    const maxValue = d3.max(matrix.flat());
                    return d3.interpolateBlues(d.value / maxValue);
                })
                .style("stroke", "#000");

            // Add cell values
            svg.selectAll(".cell-text")
                .data(matrix.flat().map((value, index) => {
                    const row = Math.floor(index / numCols);
                    const col = index % numCols;
                    return { value, row, col };
                }))
                .enter()
                .append("text")
                .attr("class", "cell-text")
                .attr("x", d => d.col * cellSize + cellSize / 2)
                .attr("y", d => d.row * cellSize + cellSize / 2)
                .attr("dy", ".35em")
                .attr("text-anchor", "middle")
                .text(d => d.value)
                .style("fill", d => (d.value > 0.5 * d3.max(matrix.flat()) ? "white" : "black")); // Adjust text color based on value

            // Add color-coded top labels
            svg.selectAll(".predicted-color")
                .data(labels)
                .enter()
                .append("line")
                .attr("class", "predicted-color")
                .attr("x1", (_, i) => i * cellSize)
                .attr("x2", (_, i) => (i + 1) * cellSize)
                .attr("y1", -10)
                .attr("y2", -10)
                .attr("stroke", (_, i) => classColors[labels[i]] || defaultColor)
                .attr("stroke-width", 10);

            // Add color-coded left labels
            svg.selectAll(".true-color")
                .data(labels)
                .enter()
                .append("line")
                .attr("class", "true-color")
                .attr("x1", -10)
                .attr("x2", -10)
                .attr("y1", (_, i) => i * cellSize)
                .attr("y2", (_, i) => (i + 1) * cellSize)
                .attr("stroke", (_, i) => classColors[labels[i]] || defaultColor)
                .attr("stroke-width", 10);

            // Add axis labels
            svg.append("text")
                .attr("class", "axis-label")
                .attr("x", matrixWidth / 2)
                .attr("y", -20)
                .attr("text-anchor", "middle")
                .text("Predicted Class");

            svg.append("text")
                .attr("class", "axis-label")
                .attr("x", -50)
                .attr("y", matrixHeight / 2 + 30)
                .attr("text-anchor", "middle")
                .attr("transform", `rotate(-90, -50, ${matrixHeight / 2})`)
                .text("True Class");
        })
        .catch(error => console.error('Error loading JSON:', error));
}

// Example call to the function
renderConfusionMatrix('http://127.0.0.1:5500/api/v1/tree/confusion-matrix?treeId=1', "#confusion-matrix-svg");
renderConfusionMatrix('/example/api/tree/confusion-matrix.json', "#confusion-matrix-svg");
