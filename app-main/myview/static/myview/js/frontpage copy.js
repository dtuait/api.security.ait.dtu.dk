console.log('Frontpage JS loaded');





// function generateToken() {
//     // Get the CSRF token
//     let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

//     fetch('/generate-token/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': csrfToken  // Set CSRF token header for Django
//         },
//     })
//     .then(response => {
//         if (response.ok) {
//             return response.json();  // Convert response to JSON if successful
//         }
//         throw new Error('Failed to generate token');  // Throw error if response is not successful
//     })
//     .then(data => {
//         console.log('Token:', data.token);  // Log the token to console
//         // You can also update the DOM to display the token to the user here
//         document.getElementById('tokenDisplay').textContent = `Your Token: ${data.token}`;
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// }










// function regenerateToken() {
//     // Get the CSRF token
//     let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

//     fetch('/regenerate-token/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': csrfToken  // Set CSRF token header for Django
//         },
//     })
//     .then(response => {
//         if (response.ok) {
//             return response.json();  // Convert response to JSON if successful
//         }
//         throw new Error('Failed to regenerate token');  // Throw error if response is not successful
//     })
//     .then(data => {
//         console.log('New Token:', data.token);  // Log the new token to console
//         // You can also update the DOM to display the new token to the user here
//         document.getElementById('tokenDisplay').textContent = `Your New Token: ${data.token}`;
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// }






async function syncADGroups() {
    const data = {
        action: 'sync_ad_groups',
        // Any other data you need to send
    };

    const response = await sendAuthenticatedAjax('/myview/ajax/', data);

    return response;



}

// syncADGroups();







document.getElementById('asyncActionButton').addEventListener('click', async function () {
    const button = this;
    const spinner = document.getElementById('loadingSpinner');


    // Show the spinner and disable the button
    spinner.style.display = 'inline-block';
    button.disabled = true;



    let response;
    try {
        response = await syncADGroups();


        // Process your response here
        // console.log(response);
    } catch (error) {
        console.error('Error:', error);

        // Optionally, show an error message to the user
    } finally {
        // Hide the spinner and enable the button
        spinner.style.display = 'none';
        button.disabled = false;
        
        if (response.success) {
            displayNotification('AD Groups synced successfully!', 'success');
        } else if (response.error) {
            displayNotification(response.error, 'warning');
        } else {
            displayNotification('An unknown error occurred.', 'warning');
        }

    }
});