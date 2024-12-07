function populateFormFromConfig(configData) {
    if (!configData) return;

    Object.entries(configData).forEach(([key, value]) => {
        const element = document.getElementById(key);

        if (Array.isArray(value)) {
            // console.log(key, value)
            if (key === "selection-criterion") {
                // Uncheck all first
                const allCheckBoxes = document.querySelectorAll('.selection-criterion');
                allCheckBoxes.forEach((checkbox) => {
                    checkbox.checked = false; // Uncheck all checkboxes initially
                });

                // Handle multiple checkboxes for selection criteria
                value.forEach((criterion) => {
                    const checkbox = document.querySelector(`input[type="checkbox"][value="${criterion}"]`);
                    // console.log(checkbox);
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
            } else if (key === "included-attributes-for-filter") {
                const seletedFilterIncludeAttirbute = document.getElementById('filter-include-attirbute');
                // Iterate through all <option> elements
                Array.from(seletedFilterIncludeAttirbute.options).forEach(option => {
                    if (value.includes(option.value)) {
                        option.selected = true; // Mark the option as selected
                    }
                });
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

    // const featureSet = document.getElementById("feature-set").value;
    // formValues["feature-set"] = featureSet ? featureSet.split(",").map((item) => item.trim()) : [];

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

    const seletedFilterIncludeAttirbute = document.getElementById('filter-include-attirbute');
    formValues["included-attributes-for-filter"] = Array.from(seletedFilterIncludeAttirbute.selectedOptions).map(option => option.value);

    return formValues;
}

async function loadAttributes() {
    try {
        const response = await window.fetcher.datasetAttributes('UCI_Census_Income_1994');
        if (response.code === 200) {
            const seletedFilterIncludeAttirbute = document.getElementById('filter-include-attirbute');
            const includeAttributesOptions = response.data;
            includeAttributesOptions.forEach(attr => {
                const option = document.createElement('option');
                option.value = attr; // Set the value
                option.textContent = attr; // Set the display text
                seletedFilterIncludeAttirbute.appendChild(option); // Add the option to the select
            });
        } else {
            console.error("Failed to fetch user configuration:", response);
        }
    } catch (error) {
        console.error("Error fetching user configuration:", error);
    }
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
    if (!maxDepthMin.value || !maxDepthMax.value || Number(maxDepthMin.value) >= Number(maxDepthMax.value) || Number(maxDepthMin.value) <= 0) {
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
    if (!stochasticSamples.value || Number(stochasticSamples.value) < 50 || Number(stochasticSamples.value) > 1000) {
        stochasticSamples.classList.add("is-invalid");
        isValid = false;
    } else {
        stochasticSamples.classList.remove("is-invalid");
    }

    // Check filter-include-attirbute
    // TODO: The front-end not implemented yet
    // const seletedFilterIncludeAttirbute = document.getElementById('filter-include-attirbute');
    // const userSelected = Array.from(seletedFilterIncludeAttirbute.selectedOptions).map(option => option.value);
    // if (userSelected.length === 0) {
    //     seletedFilterIncludeAttirbute.classList.add("is-invalid");
    //     isValid = false;
    // } else {
    //     seletedFilterIncludeAttirbute.classList.remove("is-invalid");
    // }

    return isValid;
}

function applyDefault() {
    // TODO: To be Implemented
    // const featureSet = document.getElementById("feature-set").value;
    // formValues["feature-set"] = featureSet ? featureSet.split(",").map((item) => item.trim()) : [];

    document.getElementById("max-depth-range-min").value = 1;
    document.getElementById("max-depth-range-max").value = 8;

    document.getElementById("min-leaf-size").value = 20;

    document.getElementById("round-to-significant-digit").value = 2;

    document.getElementById("stochastic-samples").value = 300;

    document.querySelectorAll('input[type="checkbox"][id^="selection-criterion"]').forEach((checkbox) => {
        checkbox.checked = true;
    });
}


document.addEventListener('DOMContentLoaded', async () => {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    await loadAttributes();
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
                    // Save user configurations
                    const response = await window.fetcher.userSetConfigs(userConfigs);
                    if (response.code === 200) {
                        console.log("User configurations saved successfully.");

                        // Start the training process
                        const trainResponse = await window.fetcher.modelTrainStart();
                        if (trainResponse.code === 200) {
                            console.log("Training started successfully.");
                            // Redirect to train-status page
                            window.location.href = "/train-status";
                        } else {
                            console.error("Failed to start training:", trainResponse);
                        }
                    } else {
                        console.error("Failed to save user configuration:", response);
                    }
                } catch (error) {
                    console.error("Error during training process:", error);
                }
            },
            onCancel: () => {
                console.log("User canceled");
            },
        });
    });

    const applyDefaultBtn = document.querySelector("#apply-default-btn");
    applyDefaultBtn.addEventListener("click", (e) => {
        e.preventDefault();
        applyDefault();
    })
});