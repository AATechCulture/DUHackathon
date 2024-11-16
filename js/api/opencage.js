import axios from 'axios';

const API_KEY = 'YOUR_API_KEY'; // Replace with your OpenCage API key
const BASE_URL = 'https://api.opencagedata.com/geocode/v1/json';

export const getGeocode = async (query) => {
  try {
    const response = await axios.get(BASE_URL, {
      params: {
        q: query,
        key: API_KEY,
      },
    });
    return response.data.results;
  } catch (error) {
    console.error('Error fetching geocode:', error);
    throw error;
  }
};
