document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const startTrainBtn = document.querySelector('#start-training-btn');
    startTrainBtn.addEventListener('click', (e, v) => {
        e.preventDefault();
        showAlert({
            title: 'Do you wish to start training?',
            message: 'Traing takes times. Once train start, you cannot abort the procedure!',
            onConfirm: () => {
                console.log('User confirmed');
                window.location.href = '/train-status'; // redirect to train-status page
            },
            onCancel: () => {
                console.log('User canceled');
            }
        });
    })
});