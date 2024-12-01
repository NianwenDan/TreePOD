function showAlert(options) {
    const { title, message, onConfirm, onCancel } = options;

    // Create overlay for darkened background
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    overlay.style.zIndex = '9998';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';

    // Create modal container
    const modalContainer = document.createElement('div');
    modalContainer.className = 'modal modal-sheet position-static d-block bg-body-secondary p-4 py-md-5';
    modalContainer.style.zIndex = '9999';

    // Create modal dialog
    const modalDialog = document.createElement('div');
    modalDialog.className = 'modal-dialog';
    modalDialog.role = 'document';

    // Create modal content
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content rounded-3 shadow';

    // Modal body
    const modalBody = document.createElement('div');
    modalBody.className = 'modal-body p-4 text-center';

    const modalTitle = document.createElement('h5');
    modalTitle.className = 'mb-0';
    modalTitle.textContent = title || 'Alert';

    const modalMessage = document.createElement('p');
    modalMessage.className = 'mb-0';
    modalMessage.textContent = message || '';

    modalBody.appendChild(modalTitle);
    modalBody.appendChild(modalMessage);

    // Modal footer
    const modalFooter = document.createElement('div');
    modalFooter.className = 'modal-footer flex-nowrap p-0';

    // Confirm button
    const confirmButton = document.createElement('button');
    confirmButton.type = 'button';
    confirmButton.className = 'btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0 border-end';
    confirmButton.innerHTML = '<strong>Yes</strong>';
    confirmButton.onclick = () => {
        if (onConfirm) onConfirm();
        document.body.removeChild(overlay);
    };

    // Cancel button
    const cancelButton = document.createElement('button');
    cancelButton.type = 'button';
    cancelButton.className = 'btn btn-lg btn-link fs-6 text-decoration-none col-6 py-3 m-0 rounded-0';
    cancelButton.textContent = 'No';
    cancelButton.onclick = () => {
        if (onCancel) onCancel();
        document.body.removeChild(overlay);
    };

    modalFooter.appendChild(confirmButton);
    modalFooter.appendChild(cancelButton);

    // Append body and footer to modal content
    modalContent.appendChild(modalBody);
    modalContent.appendChild(modalFooter);

    // Append modal content to dialog
    modalDialog.appendChild(modalContent);

    // Append modal dialog to container
    modalContainer.appendChild(modalDialog);

    // Append modal container to overlay
    overlay.appendChild(modalContainer);

    // Append overlay to body
    document.body.appendChild(overlay);
}

// Usage:
// showAlert({
//     title: 'Enable this setting?',
//     message: 'You can always change your mind in your account settings.',
//     onConfirm: () => {
//         console.log('User confirmed');
//     },
//     onCancel: () => {
//         console.log('User canceled');
//     }
// });