function populateFormFromConfig(configData) {
    if (!configData) return;

    Object.entries(configData).forEach(([key, value]) => {
        const element = document.getElementById(key);
        
        if (Array.isArray(value)) {
            console.log(key, value)
            if (key === "selection-criterion") {
                // Uncheck all first
                const allCheckBoxes = document.querySelectorAll('.selection-criterion');
                allCheckBoxes.forEach((checkbox) => {
                    checkbox.checked = false; // Uncheck all checkboxes initially
                });
                
                // Handle multiple checkboxes for selection criteria
                value.forEach((criterion) => {
                    const checkbox = document.querySelector(`input[type="checkbox"][value="${criterion}"]`);
                    console.log(checkbox);
                    if (checkbox) {
                        checkbox.checked = true;
                    }
                });
            } else if (key === "max-depth-range" && value.length === 2) {
                // Handle range fields (e.g., max-depth-range)
                const [min, max] = value;
                const minElement = document.getElementById("max-depth-range-min");
                const maxElement = document.getElementById("max-depth-range-max");
                if (minElement && maxElement) {
                    minElement.value = min;
                    maxElement.value = max;
                }
            } else {
                // Handle generic multi-value fields
                element.value = value.join(", ");
            }
        } else if (typeof value === "boolean") {
            // Handle boolean values for checkboxes
            element.checked = value;
        } else if (typeof value !== "object") {
            // Handle single-value fields
            element.value = value;
        }
    });
}

function gatherFormValues() {
    const formValues = {};

    const featureSet = document.getElementById("feature-set").value;
    formValues["feature-set"] = featureSet ? featureSet.split(",").map((item) => item.trim()) : [];

    const maxDepthMin = document.getElementById("max-depth-range-min").value;
    const maxDepthMax = document.getElementById("max-depth-range-max").value;
    formValues["max-depth-range"] = [Number(maxDepthMin), Number(maxDepthMax)];

    const minLeafSize = document.getElementById("min-leaf-size").value;
    formValues["min-leaf-size"] = minLeafSize ? Number(minLeafSize) : null;

    const pruning = document.getElementById("pruning").checked;
    formValues["pruning"] = pruning;

    const roundToSignificantDigit = document.getElementById("round-to-significant-digit").value;
    formValues["round-to-significant-digit"] = roundToSignificantDigit ? Number(roundToSignificantDigit) : null;

    const stochasticSamples = document.getElementById("stochastic-samples").value;
    formValues["stochastic-samples"] = stochasticSamples ? Number(stochasticSamples) : null;

    // Gather selection criteria from checkboxes
    const selectedCriteria = [];
    document.querySelectorAll('input[type="checkbox"][id^="selection-criterion"]').forEach((checkbox) => {
        if (checkbox.checked) {
            selectedCriteria.push(checkbox.value);
        }
    });
    formValues["selection-criterion"] = selectedCriteria;

    return formValues;
}

async function loadUserSettings() {
    try {
        const response = await window.fetcher.userGetConfig();
        if (response.code === 200) {
            populateFormFromConfig(response.data);
            console.log("User configuration loaded:", response.data);
        } else {
            console.error("Failed to fetch user configuration:", response);
        }
    } catch (error) {
        console.error("Error fetching user configuration:", error);
    }
}


document.addEventListener('DOMContentLoaded', async () => {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    await loadUserSettings();

    const startTrainBtn = document.querySelector("#start-training-btn");
    startTrainBtn.addEventListener("click", (e) => {
        e.preventDefault();

        showAlert({
            title: "Do you wish to start training?",
            message: "Training takes time. Once training starts, you cannot abort the procedure!",
            onConfirm: async () => {
                const userConfigs = gatherFormValues();
                console.log("Configurations to save:", userConfigs);

                try {
                    const response = await window.fetcher.userSetConfigs(userConfigs);
                    if (response.code === 200) {
                        window.location.href = "/train-status"; // Redirect to train-status page
                    } else {
                        console.error("Failed to save user configuration:", response);
                    }
                } catch (error) {
                    console.error("Error saving user configuration:", error);
                }
            },
            onCancel: () => {
                console.log("User canceled");
            },
        });
    });
});