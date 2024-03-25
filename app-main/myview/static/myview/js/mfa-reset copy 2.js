

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');

    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent the default form submission
        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            updateSessionStorage(data);
        })
        .then(() => {
            updateAuthenticationMethods();
        })
        .then(() => {
            console.log('Form submitted');
        })
        .catch(error => console.error('Error:', error));
    });
});

function updateSessionStorage(data) {
    // save the data to session storage    
    sessionStorage.setItem('userPrincipalObj', JSON.stringify(data));    
}





function updateAuthenticationMethods() {

    // get session storage data
    const userPrincipalObj = JSON.parse(sessionStorage.getItem('userPrincipalObj'));
    const authenticationMethods = JSON.parse(sessionStorage.getItem('userPrincipalObj')).authentication_methods[0];
    const container = document.querySelector('.container'); // Assuming you want to append the list here
    
    // Start building HTML content for userPrincipalObj
    
    let htmlContent = '<div class="user-principal-info">';
    let elementInfo = document.querySelector('.user-principal-info');
    if (elementInfo) {
        elementInfo.remove();
    }
    const fields = ['displayName', 'givenName', 'id', 'jobTitle', 'mail', 'mobilePhone', 'officeLocation', 'surname', 'userPrincipalName'];

    for (const field of fields) {
        const value = userPrincipalObj[field];
        if (value !== undefined) {
            // Handle array values differently to concatenate their contents
            if (Array.isArray(value)) {
                htmlContent += `<div><strong>${field}:</strong> ${value.join(', ')}</div>`;
            } else {
                htmlContent += `<div><strong>${field}:</strong> ${value}</div>`;
            }
        }
    }
    htmlContent += '</div>'; // Close the user principal info div

    // Continue with building HTML content for authentication methods
    htmlContent += '<div class="auth-methods-list">';
    let elementAuth = document.querySelector('.auth-methods-list');
    if (elementAuth) {
        elementAuth.remove();
    }
    authenticationMethods.value.forEach(method => {
        let methodDiv = '<div class="auth-method my-4">';
        for (const [key, value] of Object.entries(method)) {
            // if (key !== '@odata.type') { // Skip the @odata.type property
                methodDiv += `<span><strong>${key}:</strong> ${value}</span><br>`;
            // }
        }

        // only add button if the @odata.type property contains '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod'
        if (method['@odata.type'] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
            // methodDiv += `<button class="btn btn-danger remove-btn" data-method-id="${method.id}">Remove</button>`;
            methodDiv += `<button class="btn btn-danger remove-btn" data-method-id="${method.id}" data-bs-toggle="modal" data-bs-target="#deleteConfirmationModal">Remove</button>`;

        } else {
            methodDiv += `<button type="button" class="btn btn-info" data-bs-toggle="modal" data-bs-target="#infoModal">Info</button>`;
        }

        methodDiv += '</div>';
        htmlContent += methodDiv;
    });
    htmlContent += '</div>'; // Close the auth methods list div

    // container.innerHTML += htmlContent; // Replace the container's content
    container.insertAdjacentHTML('beforeend', htmlContent); // Append the new HTML
}


var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"][data-bs-html="true"]'))
tooltipTriggerList.forEach(function (tooltipTriggerEl) {
  new bootstrap.Tooltip(tooltipTriggerEl, {
    html: true  // Enables HTML content inside tooltips
  });
});

document.getElementById('confirmDelete').addEventListener('click', function() {
    // const methodId = window.methodIdToDelete; // The ID captured when the remove button is clicked
    // const csrftoken = getCookie('csrftoken'); // Function to get CSRF token from cookies


    const authentication_id = window.methodIdToDelete; // The ID captured when the remove button is clicked
    const user_principal_id = JSON.parse(sessionStorage.getItem('userPrincipalObj')).id;
    const csrftoken = getCookie('csrftoken'); // Function to get CSRF token from cookies
    
    

    // const deleteUrl = `${deleteAuthMethodUrlPattern}${authentication_id}/`; // Assuming methodId is available
    // const deleteUrl = `/app-main/myview/delete-authentication-method/${user_principal_id}/${authentication_id}/`; // Assuming methodId is available
    // const deleteUrl = `/myview/mfa-reset/user/${user_principal_id}/delete-authentication/${authentication_id}/`;
    //                         mfa-reset/user/<str:user_principal_id>/delete-authentication/<str:authentication_id>/

    const protocol = window.location.protocol;
    const host = window.location.host;
    const path = `/myview/mfa-reset/user/${user_principal_id}/delete-authentication/${authentication_id}/`;
    const deleteUrl = `${protocol}//${host}${path}`;
        

    fetch(deleteUrl, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
    })
    .then(() => {
        // updateSessionStorage();
        updateAuthenticationMethods();
        displayNotification('The authentication method was successfully deleted.', 'success');

       // Programmatically hide the modal after successful deletion
       const deleteConfirmationModal = document.getElementById('deleteConfirmationModal');
       const bootstrapModal = bootstrap.Modal.getInstance(deleteConfirmationModal);
       bootstrapModal.hide();
    })
    .catch(error => {
        console.error('There was a problem with the delete request:', error);
        displayNotification('Error deleting the authentication method.', 'error');
    });
});

// Utility function to get a cookie value by name
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}























function displayNotification(message, type) {
    const alertType = type === 'success' ? 'alert-success' : 'alert-warning';
    const notificationHtml = `<div class="alert ${alertType} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;

    const notificationsContainer = document.getElementById('notifications-container');
    notificationsContainer.innerHTML = notificationHtml; // Add the notification to the container
}











// To capture the method ID before showing the modal
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-btn')) {
        window.methodIdToDelete = e.target.getAttribute('data-method-id'); // Store method ID globally
    }
});











































// function updateAuthenticationMethods(data) {

//     const authenticationMethods = data.authenticationMethods;
//     const userPrincipalObj = data



//     const container = document.querySelector('.container'); // Assuming you want to append the list here
//     let htmlContent = '<div class="auth-methods-list">';


//     authenticationMethods[0].value.forEach(method => {
//         // Start the div for this auth method
//         let methodDiv = `<div class="auth-method">`;
    
//         // Add a span for each property in the method, except for '@odata.type'
//         for (const [key, value] of Object.entries(method)) {
//             if (key !== '@odata.type') { // Skip the @odata.type property
//                 methodDiv += `<span><strong>${key}:</strong> ${value}</span><br>`;
//             }
//         }
    
//         // Add the remove button with the method's ID
//         methodDiv += `<button class="btn btn-danger remove-btn" data-method-id="${method.id}">Remove</button>`;
    
//         // Close the div
//         methodDiv += `</div>`;
    
//         // Append this method's div to the overall HTML content
//         htmlContent += methodDiv;
//     });

//     htmlContent += '</div>';
//     container.innerHTML += htmlContent; // Append the new HTML
// }