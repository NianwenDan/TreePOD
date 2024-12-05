async function checkIfUserExists() {
    try {
        const response = await window.fetcher.systemGetUserId();
        if (response.code === 200) {
            const userId = response["userId"];
            console.log(`userId: ${userId}`);
            if (userId) {
                return true
            }
            window.location.href = '/get-started';
        } else {
            console.error("Failed to fetch user configuration:", response);
            window.location.href = '/get-started';
        }
    } catch (error) {
        console.error("Error fetching user configuration:", error);
        window.location.href = '/get-started';
    }
}

async function checkIfUserTrainedModel() {
    try {
        const response = await window.fetcher.modelTrainStatus();
        if (response.code === 200) {
            const code = response.data["code"];
            if (code === 0) {
                console.log(`Trained: True`);
                return true
            }
            console.log(`Trained: False`);
            window.location.href = '/settings';
            return false
        } else {
            console.error("Failed to fetch user configuration:", response);
            window.location.href = '/settings';
        }
    } catch (error) {
        console.error("Error fetching user configuration:", error);
        window.location.href = '/settings';
    }
}