function createSummaryPanel(data) {
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
}