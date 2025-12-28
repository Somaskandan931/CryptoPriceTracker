import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json"
  }
});

// Add response interceptor for error handling
API.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.message);
    return Promise.reject(error);
  }
);

// Changed from /coins to /assets
export const fetchCoins = () => API.get("/assets");

export const fetchPrediction = (asset, daysAhead = 1) => {
  return API.get(`/predict/${asset}`, {
    params: {
      days_ahead: daysAhead
    }
  });
};

export const fetchAssetDetails = (asset) => API.get(`/asset/${asset}`);

export default API;