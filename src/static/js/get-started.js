document.addEventListener('DOMContentLoaded', async () => {
  const loadingSpinner = document.getElementById('loading-spinner');
  const radioContainer = document.getElementById('radio-container');
  const radioForm = document.getElementById('radio-form');
  const submitButton = document.getElementById('submit-btn');
  const card = document.querySelector('.card'); // Select the card element

  try {
    // Simulate fetching system status
    const systemStatus = await window.fetcher.systemStatus();
    if (systemStatus.code !== 200) {
      console.error('System is not OK:', systemStatus.msg);
      alert('System is not ready. Please try again later.');
      return;
    }

    // Simulate fetching radio button data
    const dataResponse = await window.fetcher.datasetList();
    if (dataResponse.code === 200 && Array.isArray(dataResponse.data)) {
      // Remove the spinner
      loadingSpinner.style.display = 'none';

      card.classList.remove('align-items-center', 'justify-content-center');

      // Display the form
      radioForm.style.display = 'block';

      // Dynamically create radio buttons based on the data
      dataResponse.data.forEach((item, index) => {
        const radioId = `radio-${index}`;
        const radioInput = document.createElement('input');
        radioInput.type = 'radio';
        radioInput.className = 'btn-check';
        radioInput.name = 'vbtn-radio';
        radioInput.id = radioId;
        radioInput.value = item;

        const radioLabel = document.createElement('label');
        radioLabel.className = 'btn btn-outline-dark';
        radioLabel.htmlFor = radioId;
        radioLabel.textContent = item;

        radioContainer.appendChild(radioInput);
        radioContainer.appendChild(radioLabel);
      });

      // Enable submit button when a radio is selected
      const radioButtons = document.querySelectorAll('input[name="vbtn-radio"]');
      radioButtons.forEach((radio) => {
        radio.addEventListener('change', () => {
          submitButton.disabled = !Array.from(radioButtons).some(radio => radio.checked);
        });
      });
    } else {
      console.error('Failed to fetch data:', dataResponse.msg);
      alert('Unable to load options. Please try again later.');
    }

    // Handle form submission
    radioForm.addEventListener('submit', async (event) => {
      event.preventDefault(); // Prevent default form submission
      try {
        // Find which dataset being selected and then pass through to systemSetUserId()
        const selectedRadio = document.querySelector('input[name="vbtn-radio"]:checked');
        const selectedDataset = selectedRadio.value.replace(/ /g, '_');
        
        const userIdResponse = await window.fetcher.systemSetUserId(selectedDataset);
        if (userIdResponse.code === 200) {
          // Redirect to the settings
          window.location.href = '/settings';
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
