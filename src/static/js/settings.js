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

function validateForm() {
    let isValid = true;

    // Check feature set (disabled inputs should not be required)
    const featureSet = document.getElementById("feature-set");
    if (!featureSet.disabled && featureSet.value.trim() === "") {
        featureSet.classList.add("is-invalid");
        isValid = false;
    } else {
        featureSet.classList.remove("is-invalid");
    }

    // Check selection criterion (at least one checkbox must be checked)
    const selectionCriteria = document.querySelectorAll(".selection-criterion");
    const isAnyCriterionChecked = Array.from(selectionCriteria).some((checkbox) => checkbox.checked);
    if (!isAnyCriterionChecked) {
        const feedbacks = document.querySelectorAll('.selection-criterion');
        feedbacks.forEach((feedback) => {
            feedback.classList.add("is-invalid");
            const invalidFeedback = feedback.nextElementSibling;
            if (invalidFeedback && invalidFeedback.classList.contains("invalid-feedback")) {
                invalidFeedback.style.display = 'block';
            }
        });
        isValid = false;
    } else {
        const feedbacks = document.querySelectorAll('.selection-criterion');
        feedbacks.forEach((feedback) => {
            feedback.classList.remove("is-invalid");
            const invalidFeedback = feedback.nextElementSibling;
            if (invalidFeedback && invalidFeedback.classList.contains("invalid-feedback")) {
                invalidFeedback.style.display = 'none';
            }
        });
    }

    // Check max-depth-range
    const maxDepthMin = document.getElementById("max-depth-range-min");
    const maxDepthMax = document.getElementById("max-depth-range-max");
    if (!maxDepthMin.value || !maxDepthMax.value || Number(maxDepthMin.value) >= Number(maxDepthMax.value)) {
        maxDepthMin.classList.add("is-invalid");
        maxDepthMax.classList.add("is-invalid");
        isValid = false;
    } else {
        maxDepthMin.classList.remove("is-invalid");
        maxDepthMax.classList.remove("is-invalid");
    }

    // Check min-leaf-size
    const minLeafSize = document.getElementById("min-leaf-size");
    if (!minLeafSize.value || Number(minLeafSize.value) <= 0) {
        minLeafSize.classList.add("is-invalid");
        isValid = false;
    } else {
        minLeafSize.classList.remove("is-invalid");
    }

    // Check round-to-significant-digit
    const roundToSignificantDigit = document.getElementById("round-to-significant-digit");
    if (!roundToSignificantDigit.value || Number(roundToSignificantDigit.value) <= 0) {
        roundToSignificantDigit.classList.add("is-invalid");
        isValid = false;
    } else {
        roundToSignificantDigit.classList.remove("is-invalid");
    }

    // Check stochastic-samples
    const stochasticSamples = document.getElementById("stochastic-samples");
    if (!stochasticSamples.value || Number(stochasticSamples.value) < 100) {
        stochasticSamples.classList.add("is-invalid");
        isValid = false;
    } else {
        stochasticSamples.classList.remove("is-invalid");
    }

    return isValid;
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

        // Perform validation
        const isValid = validateForm();

        if (!isValid) {
            console.error("Validation failed. Please correct the errors.");
            return;
        }

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