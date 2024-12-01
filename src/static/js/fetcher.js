// fetcher.js
const BASE_URL = 'http://127.0.0.1:5500/api/v1'; // Replace with your API base URL

/**
 * Helper function to make API requests
 * @param {string} endpoint - The API endpoint (relative to BASE_URL)
 * @param {object} options - Fetch options (e.g., method, headers, body)
 * @returns {Promise<any>} - The response data
 */
const fetchData = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      credentials: 'include', // Ensures cookies are sent with requests
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Fetch error for ${endpoint}:`, error);
    throw error;
  }
};

/**
 * Helper function to make POST API requests with JSON payload
 * @param {string} endpoint - The API endpoint (relative to BASE_URL)
 * @param {object} jsonData - The JSON payload to send
 * @returns {Promise<any>} - The response data
 */
const postData = async (endpoint, jsonData) => {
  return fetchData(endpoint, {
    method: 'POST',
    body: JSON.stringify(jsonData),
  });
};

// Define global functions for specific endpoints
window.fetcher = {
  systemStatus: () => fetchData('/system/status'),
  systemSetUserId: () => fetchData('/system/set-userId'),
  systemGetUserId: () => fetchData('/system/get-userId'),
  userGetConfig: () => fetchData('/user/get-config'),
  userGetRandomConfig: () => fetchData('/user/get-random-config'),
  userSetConfigs: (data) => postData('/user/set-configs', data),
  datasetList: () => fetchData('/dataset/list'),
  modelTrainStart: () => fetchData('/model/train-start'),
  modelTrainStatus: () => fetchData('/model/train-status'),
  modelTrees: () => fetchData('/model/trees'),
  treeStructure: () => fetchData('/tree/structure?treeId=1'),
  treeConfusionMatrix: () => fetchData('/tree/confusion-matrix?treeId=1'),
};
