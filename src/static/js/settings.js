document.addEventListener('DOMContentLoaded', async () => {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Helper function to set or get form field values
    function handleFormFields(configData = null) {
        const fields = {
            "selection-criterion": "criterion",
            "max-depth": "max_depth",
            "stochastic-samples": "total_samples",
            "pruning": "ccp_alpha",
            "additional-features": "min_samples_split",
            "training-data": "random_state"
        };

        if (configData) {
            // Populate form fields with configData
            Object.keys(fields).forEach(fieldId => {
                const configKey = fields[fieldId];
                if (configData[configKey] !== undefined) {
                    document.getElementById(fieldId).value = configData[configKey];
                }
            });
        } else {
            // Retrieve form field values into an object
            const formValues = {};
            Object.keys(fields).forEach(fieldId => {
                const configKey = fields[fieldId];
                const fieldValue = document.getElementById(fieldId).value;
                if (fieldValue) {
                    formValues[configKey] = fieldValue;
                }
            });
            return formValues;
        }
    }

    // Load user settings on page load
    async function loadUserSettings() {
        try {
            const userConfigResponse = await window.fetcher.userGetConfig();
            if (userConfigResponse.code === 200) {
                const userConfigData = userConfigResponse.data;
                handleFormFields(userConfigData); // Populate the form with user settings
                console.log("User configuration loaded:", userConfigData);
            } else {
                console.error("Failed to fetch user configuration:", userConfigResponse);
            }
        } catch (error) {
            console.error("Error fetching user configuration:", error);
        }
    }

    // Call the function to load user settings
    await loadUserSettings();

    const startTrainBtn = document.querySelector('#start-training-btn');
    startTrainBtn.addEventListener('click', (e, v) => {
        e.preventDefault();
        showAlert({
            title: 'Do you wish to start training?',
            message: 'Traing takes times. Once train start, you cannot abort the procedure!',
            onConfirm: async () => {
                console.log('User confirmed');
                const userConfigs = handleFormFields();
                const response = await window.fetcher.userSetConfigs(userConfigs);
                if (response.code == 200) {
                    window.location.href = '/train-status'; // redirect to train-status page
                }
            },
            onCancel: () => {
                console.log('User canceled');
            }
        });
    })

    const generateRandomConfigBtn = document.querySelector('#generate-random-config-btn');
    generateRandomConfigBtn.addEventListener('click', async (e, v) => {
        e.preventDefault();
        try {
            const dataResponse = await window.fetcher.userGetRandomConfig();
            if (dataResponse.code === 200) {
                const randomConfigData = dataResponse.data;

                // Populate form with random config values
                handleFormFields(randomConfigData);
                console.log("Random configuration applied:", randomConfigData);
            } else {
                console.error("Failed to fetch random config:", dataResponse);
            }
        } catch (error) {
            console.error("Error fetching random config:", error);
        }
    })
});