document.addEventListener("DOMContentLoaded", function () {
    const progressBar = document.querySelector('.progress-bar');
    const loadingDiv = document.getElementById('loading');
    const contentDiv = document.getElementById('content');

    // Function to update the progress bar based on the API response
    const updateProgressBar = (progress) => {
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
        progressBar.textContent = `${progress}%`;
    };

    // Function to poll the modelTrainStatus API
    const pollTrainingStatus = async () => {
        try {
            const response = await window.fetcher.modelTrainStatus();
            if (response.code === 200) {
                const data = response.data;

                // Calculate the progress percentage
                const progress = Math.floor((data.number_of_samples_trained / data.total_number_of_samples) * 100);

                // Update the progress bar
                updateProgressBar(progress);

                // Check if training is complete
                if (data.number_of_samples_trained === data.total_number_of_samples) {
                    clearInterval(interval); // Stop polling
                    loadingDiv.style.display = 'none'; // Hide the loading spinner
                    contentDiv.style.display = 'block'; // Show the main content
                    setTimeout(() => {
                        window.location.href = '/dashboard'; // Redirect to /dashboard
                    }, 1000); // Redirect after a brief delay for smoother transition
                }
            } else {
                console.error("Error fetching training status:", response.msg);
            }
        } catch (error) {
            console.error("Error during API call:", error);
        }
    };

    // Start polling every second
    const interval = setInterval(pollTrainingStatus, 500);
});
