console.log('Frontpage JS loaded');

function generateToken() {
    // Get the CSRF token
    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/generate-token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // Set CSRF token header for Django
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();  // Convert response to JSON if successful
        }
        throw new Error('Failed to generate token');  // Throw error if response is not successful
    })
    .then(data => {
        console.log('Token:', data.token);  // Log the token to console
        // You can also update the DOM to display the token to the user here
        document.getElementById('tokenDisplay').textContent = `Your Token: ${data.token}`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function regenerateToken() {
    // Get the CSRF token
    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/regenerate-token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // Set CSRF token header for Django
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();  // Convert response to JSON if successful
        }
        throw new Error('Failed to regenerate token');  // Throw error if response is not successful
    })
    .then(data => {
        console.log('New Token:', data.token);  // Log the new token to console
        // You can also update the DOM to display the new token to the user here
        document.getElementById('tokenDisplay').textContent = `Your New Token: ${data.token}`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}