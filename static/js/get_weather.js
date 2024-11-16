document.getElementById('weather-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const city = document.getElementById('city').value.trim();
    const zipCode = document.getElementById('zip_code').value.trim();

    if (!city || !zipCode) {
        alert("Please enter both City and Zip Code");
        return;
    }

    try {
        // Send POST request to the Flask backend
        const response = await fetch('/get_weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ city, zip_code: zipCode }),
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        // Display weather results
        displayWeather(data);

        // Show map
        displayMap(data.latitude, data.longitude);
    } catch (error) {
        console.error("Error fetching weather data:", error);
        alert("Failed to fetch weather data. Please try again later.");
    }
});

// Display weather information
function displayWeather(data) {
    const resultsDiv = document.getElementById('weather-results');
    resultsDiv.innerHTML = `
        <h4>Weather for ${data.city}, ${data.zip_code}:</h4>
        <p>Latitude: ${data.latitude}, Longitude: ${data.longitude}</p>
        <p>Max Temperature: ${data.weather.temperature_2m_max.join(', ')} °F</p>
        <p>Min Temperature: ${data.weather.temperature_2m_min.join(', ')} °F</p>
        <p>Precipitation: ${data.weather.precipitation_sum.join(', ')} mm</p>
        <p>Flood Alerts: ${Array.isArray(data.flood_alerts) ? data.flood_alerts.length : data.flood_alerts}</p>
    `;
}

// Display map using Leaflet.js
function displayMap(lat, lon) {
    const mapDiv = document.getElementById('map');
    mapDiv.innerHTML = ''; // Clear previous map content

    const map = L.map(mapDiv).setView([lat, lon], 13);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    // Add marker for the location
    L.marker([lat, lon]).addTo(map)
        .bindPopup(`Latitude: ${lat}<br>Longitude: ${lon}`)
        .openPopup();
}
