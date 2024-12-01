document.addEventListener("DOMContentLoaded", function () {
    const progressBar = document.querySelector('.progress-bar');
    const loadingDiv = document.getElementById('loading');
    const contentDiv = document.getElementById('content');
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10; // Increase progress by 10% every second
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
        progressBar.textContent = `${progress}%`;
        if (progress >= 100) {
            clearInterval(interval); // Stop the interval when progress reaches 100%
            loadingDiv.style.display = 'none'; // Hide the loading spinner
            contentDiv.style.display = 'block'; // Show the main content
            setTimeout(() => {
                window.location.href = '/dashboard'; // Redirect to /dashboard
            }, 1000); // Redirect after a brief delay for smoother transition
        }
    }, 1000); // Update every second
});
