document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('weather-form').addEventListener('submit', async (e) => {
      e.preventDefault(); // Prevent page refresh
      const city = document.getElementById('city').value;
      const zip_code = document.getElementById('zip_code').value;

      // Clear previous results
      const resultsDiv = document.getElementById('weather-results');
      resultsDiv.innerHTML = '<p>Loading...</p>';

      try {
        // Make a POST request to the Flask API
        const response = await fetch('/get_weather', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ city, zip_code }),
        });

        const data = await response.json();

        // Check for errors
        if (data.error) {
          resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
          return;
        }

        // Display the weather and flood alert data
        resultsDiv.innerHTML = `
          <h3>Results for ${data.city}, ${data.zip_code}</h3>
          <p><strong>Latitude:</strong> ${data.latitude}</p>
          <p><strong>Longitude:</strong> ${data.longitude}</p>
          <h4>Weather</h4>
          <p><strong>Max Temperature:</strong> ${data.weather.temperature_2m_max.join(', ')} °F</p>
          <p><strong>Min Temperature:</strong> ${data.weather.temperature_2m_min.join(', ')} °F</p>
          <p><strong>Precipitation:</strong> ${data.weather.precipitation_sum.join(', ')} mm</p>
          <h4>Flood Alerts</h4>
          <p>${data.flood_alerts && data.flood_alerts.length > 0 ? data.flood_alerts.map(alert => alert.description).join('<br>') : 'No active flood alerts'}</p>
        `;
      } catch (error) {
        resultsDiv.innerHTML = `<p style="color: red;">Failed to fetch data. Please try again later.</p>`;
      }
    });
  });
