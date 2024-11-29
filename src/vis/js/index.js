document.addEventListener('DOMContentLoaded', async () => {
    const datasetSelector = document.getElementById('dataset-selector');
    const submitButton = document.querySelector('button[type="submit"]');
  
    try {
      // Check system status
      const systemStatus = await window.fetcher.systemStatus();
      if (systemStatus.code !== 200) {
        console.error('System is not OK:', systemStatus.msg);
        alert('System is not ready. Please try again later.');
        return;
      }
  
      // If system is OK, fetch datasets
      const datasetResponse = await window.fetcher.datasetList();
      if (datasetResponse.code === 200 && Array.isArray(datasetResponse.data)) {
        // Populate the dataset selector with options
        datasetSelector.disabled = false; // Enable the select element
        datasetResponse.data.forEach((dataset) => {
          const option = document.createElement('option');
          option.value = dataset;
          option.textContent = dataset;
          datasetSelector.appendChild(option);
        });
      } else {
        console.error('Failed to fetch datasets:', datasetResponse.msg);
        alert('Unable to load datasets. Please try again later.');
      }
  
      // Enable submit button when a dataset is selected
      datasetSelector.addEventListener('change', () => {
        if (datasetSelector.value) {
          submitButton.disabled = false;
        } else {
          submitButton.disabled = true;
        }
      });
  
      // Handle form submission
      document.querySelector('form').addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent the default form submission behavior
        try {
          // Call systemSetUserId
          const userIdResponse = await window.fetcher.systemSetUserId();
          if (userIdResponse.code === 200) {
            // Redirect to the dashboard
            window.location.href = '/dashboard';
          } else {
            console.error('Failed to set user ID:', userIdResponse.msg);
            alert('Failed to proceed. Please try again.');
          }
        } catch (error) {
          console.error('Error during submission:', error);
          alert('An error occurred. Please try again.');
        }
      });
    } catch (error) {
      console.error('Error during initialization:', error);
      alert('An error occurred while initializing the page.');
    }
  });
  