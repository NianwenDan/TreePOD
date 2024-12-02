class ParetoAnalysis {
    constructor(candidates) {
        this.candidates = candidates;
        this.paretoFront = {};
        this.attributes = ["depth", "f1_score", "number_of_nodes", "number_of_leaves", "number_of_used_attributes"];
        this.attributePairs = this.generateAttributePairs(this.attributes);
        this.maximizeAttributes = new Set(["f1_score"]); // Set of attributes to maximize
    }

    // Helper function to generate pairs of attributes
    generateAttributePairs(attributes) {
        const pairs = [];
        for (let a of attributes) {
            for (let b of attributes) {
                if (a !== b) pairs.push([a, b]);
            }
        }
        return pairs;
    }

    // Function to find Pareto-optimal tree IDs
    findParetoOptimal(attribute1, attribute2) {
        const dataPoints = this.candidates.map(candidate => [
            this.roundValue(
                this.maximizeAttributes.has(attribute1)
                    ? -this.getAttributeValue(candidate, attribute1)
                    : this.getAttributeValue(candidate, attribute1)
            ),
            this.roundValue(
                this.maximizeAttributes.has(attribute2)
                    ? -this.getAttributeValue(candidate, attribute2)
                    : this.getAttributeValue(candidate, attribute2)
            ),
            candidate.tree_id
        ]);
    
        const paretoFront = [];
        const seen = new Set();
    
        for (let i = 0; i < dataPoints.length; i++) {
            const point = dataPoints[i];
            let isDominated = false;
    
            for (let j = 0; j < dataPoints.length; j++) {
                if (i === j) continue;
                const otherPoint = dataPoints[j];
    
                if (
                    (otherPoint[0] <= point[0] && otherPoint[1] <= point[1]) &&
                    (otherPoint[0] < point[0] || otherPoint[1] < point[1])
                ) {
                    isDominated = true;
                    break;
                }
            }
    
            if (!isDominated) {
                const pointKey = `${point[0]}_${point[1]}`;
                if (!seen.has(pointKey)) {
                    seen.add(pointKey);
                    paretoFront.push(point);
                }
            }
        }
    
        //console.log("Pareto Front:", paretoFront);
        return paretoFront.map(p => parseInt(p[2], 10));
    }    

    // Helper function to retrieve attribute value
    getAttributeValue(candidate, attribute) {
        //console.log(attribute, candidate[attribute], candidate.predicted, candidate.predicted[attribute])
        return candidate[attribute] || (candidate.predicted && candidate.predicted[attribute]) || 0;
    }

    // Helper function to round values
    roundValue(value, precision = 3) {
        return parseFloat(value.toFixed(precision));
    }

    // Perform Pareto analysis
    paretoAnalysis() {
        const normalizedPairs = new Set(
            this.attributePairs.map(pair => pair.sort().join("__"))
        );

        for (let key of normalizedPairs) {
            const [attribute1, attribute2] = key.split("__");
            if (!this.paretoFront[key]) {
                this.paretoFront[key] = this.findParetoOptimal(attribute1, attribute2);
            }
        }
    }
}

function recomputeFilteredParetoFront() {
    const paretoAnalysis = new ParetoAnalysis(data.candidates);
    paretoAnalysis.paretoAnalysis();
    data.pareto_front = paretoAnalysis.paretoFront;
    console.log('data.paretoFront: ', data.pareto_front);
    console.log('all_data.paretoFront: ', all_data.pareto_front);
}