/*let summaryDiv = d3.select("#filter-summary");
if (summaryDiv.empty()) {
    summaryDiv = d3.select("body").append("div").attr("id", "filter-summary");
}*/
let innerSummaryPanel = d3.select("#summary-panel").append("div")
.attr("class", "inner-summary-panel")
.style("margin", "20px");

function createSummaryPanel(data) {    
    // Row 1: Display Total Candidates before Pruning
    innerSummaryPanel.append("div").attr("class", "row").style("padding", "10px").style("border-bottom", "1px solid black").html(`<strong>${data.total_candidates_before_pruning} tree candidates generated</strong>`);
    //innerSummaryPanel.append("br");

    // Placeholder Rows 2 - 3 with bottom border
    innerSummaryPanel.append("div").attr("class", "row").style("padding", "10px").style("border-bottom", "1px solid black").html(`<strong>Generation Parameter Filters (${data.total_candidates_before_pruning} trees)</strong>`);
    //innerSummaryPanel.append("br");
    displayFilterSummary(innerSummaryPanel);

    // Last row without bottom border
    innerSummaryPanel.append("div").attr("class", "row pareto-optimal").style("padding", "10px").html(`<strong>Pareto optimal: ${paretoFrontTreeNum} trees</strong>`);
    innerSummaryPanel.append("div").attr("class", "row pareto-attributes").style("padding-bottom", "10px").html(`(for ${xAttribute}, ${yAttribute})`);
    //innerSummaryPanel.append("br");
}

function updateSummaryPanel() {
    // Update the Pareto optimal tree number
    d3.select(".pareto-optimal").html(`<strong>Pareto optimal: ${paretoFrontTreeNum} trees</strong>`);
    d3.select(".pareto-attributes").html(`&nbsp;&nbsp;&nbsp;&nbsp;(for ${xAttribute}, ${yAttribute})`);
}

// Function to display all current filters
function displayFilterSummary(summaryDiv) {
    // Clear existing summary content
    //console.log('summaryDiv: ', summaryDiv);
    summaryDiv.selectAll(".filter-summary-row").remove();

    // Display each filter condition
    const filters = Object.keys(filterConditions);
    //console.log('filters: ', filterConditions);
    if (filters.length > 0) {
        summaryDiv.append("div").attr("class", "row filter-summary-row").style("padding", "10px").style("border-top", "1px solid black").html(`<strong>Result Metric Filters (${data.candidates.length}&nbsp;trees)</strong>`);
        filters.forEach((key) => {
            summaryDiv.append("div").attr("class", "row filter-summary-row").style("padding-bottom", "5px").html(`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${key}&nbsp;${filterConditions[key].sign}&nbsp;${filterConditions[key].value}`);
        }
    );
    }
    //summaryDiv.append("br");
}