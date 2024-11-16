document.getElementById('floodForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const userInput = document.getElementById('userInput').value;
    console.log("User Input: " + userInput);

    // Send a request to your Python backend (e.g., using Fetch API)
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ userInput: userInput })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output').innerText = JSON.stringify(data);
    })
    .catch(error => console.error('Error:', error));
});
