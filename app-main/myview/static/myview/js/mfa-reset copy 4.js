console.log('MFA Reset JS loaded');





async function getUserAuthenticationMethods(userEmail) {
    const url = `/v1.0/graph/list/${encodeURIComponent(userEmail)}/authentication-methods`;

    try {
        const response = await restAjax('GET', url);
        console.log('User Authentication Methods:', response);
        return response;
    } catch (error) {
        console.error('Error fetching user authentication methods:', error);
        throw error; // Allowing the caller to handle errors
    }
}


async function getUserInfo(userEmail) {
    const url = `/v1.0/graph/get-user/${encodeURIComponent(userEmail)}`;
  
    try {
        const response = await restAjax('GET', url);
        console.log('User Info:', response);
        return response;
    } catch (error) {
        console.error('Error fetching user info:', error);
        throw error; // Allowing the caller to handle errors
    }
  }

// Example usage
// result = getUserInfo('vicre-test01@dtudk.onmicrosoft.com');

$(document).ready(function() {
    $('#mfa-user-lookup-submit-btn').on('click', async function () {
        const button = $(this);
        const spinner = $('#loadingSpinner');

        // Show the spinner and disable the button
        spinner.show();
        button.prop('disabled', true);


        let userAuthenticationMethods;
        try {


            const userEmail = $('#id_username').val();
            if (!userEmail) {
                return;
            }

            const userInfo = await getUserInfo(userEmail);
            userAuthenticationMethods = await getUserAuthenticationMethods(userEmail);

            const container = $('#dataContainer');
            container.empty();
            userAuthenticationMethods.value.forEach(method => {
                
                // '2024-03-12T13:25:21Z' should be converted into MM:HH dd-mm-yyyy
                const date = new Date(method.createdDateTime);
                const formattedDate = date.toLocaleString('en-GB', { timeZone: 'UTC' });
                console.log(formattedDate);


                const protocol = window.location.protocol;
                const server = window.location.hostname;
                const port = window.location.port;


                // Variables that may change based on conditions
                let buttonClassSuffix;
                let enabledOrDisabled;
                let modalOptions = {}


                // Determine the variables based on the method type
                if (method['@odata.type'] === '#microsoft.graph.passwordAuthenticationMethod') {
                    buttonClassSuffix = 'password';
                    modalOptions.title = 'Password Authentication Method';
                    modalOptions.body = `
                    This authentication method is disabled because it is not an MFA method. If you want to DELETE it, you can do it via the API:<br>
                    <a href="${protocol}//${server}:${port}/myview/swagger/">${protocol}//${server}:${port}/myview/swagger/</a>
                    `;
                    enabledOrDisabled = 'disabled';
                } else if (method['@odata.type'] !== '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
                    buttonClassSuffix = 'notmfa';
                    modalOptions.title = 'Not MFA Method';

                    modalOptions.body = `
                    This authentication method is disabled because it is not an MFA method. If you want to DELETE it, you can do it via the API:<br>
                    <a href="${protocol}//${server}:${port}/myview/swagger/">${protocol}//${server}:${port}/myview/swagger/</a>
                    `;
                    enabledOrDisabled = 'disabled';
                } else {
                    buttonClassSuffix = 'ismfa';
                    modalOptions.title = 'MFA Method';
                    modalOptions.body = `
                    This is authentication method is MFA.
                `;
                    enabledOrDisabled = '';
                }

                // Now, construct the unique IDs based on the determined variables
                const buttonId = `btn-${buttonClassSuffix}-${method.id}`;
                const modalId = `modal-${buttonClassSuffix}-${method.id}`;
                

                // Construct the card with dynamic parts
                let card = `
                    <div class="card my-2">
                        <div class="card-body">
                            <h5 class="card-title">${method['@odata.type']}</h5>
                            <p class="card-text">ID: ${method.id}</p>
                            <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
                            <button class="btn btn-danger ${enabledOrDisabled}">Remove</button>
                            <button class="btn btn-info cardinfo-${buttonClassSuffix}" id="${buttonId}">Info</button>
                        </div>
                    </div>
                `;

                container.append(card);
                setModal(`#${buttonId}`, modalId, modalOptions);
                







                // let card;
                // const modalContent = 'Your modal content here'; // This should be replaced with actual content

                // if (method['@odata.type'] === '#microsoft.graph.passwordAuthenticationMethod') {
                //     const modalId = `modal-password-${method.id}`; // Creating a unique ID for the modal
                //     card = `
                //         <div class="card my-2">
                //             <div class="card-body">
                //                 <h5 class="card-title">${method['@odata.type']}</h5>
                //                 <p class="card-text">ID: ${method.id}</p>
                //                 <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
                //                 <button class="btn btn-danger disabled">Remove</button>
                //                 <button class="btn btn-info cardinfo-password" id="btn-password-${method.id}">Info</button>
                //             </div>
                //         </div>
                //     `;
                //     // Using the button's unique ID as the trigger selector
                //     setModal(`#btn-password-${method.id}`, modalContent, modalId);
                // }
                // else if (method['@odata.type'] !== '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
                //     const modalId = `modal-notmfa-${method.id}`; // Unique ID for the modal
                //     card = `
                //         <div class="card my-2">
                //             <div class="card-body">
                //                 <h5 class="card-title">${method['@odata.type']}</h5>
                //                 <p class="card-text">ID: ${method.id}</p>
                //                 <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
                //                 <button class="btn btn-danger disabled">Remove</button>
                //                 <button class="btn btn-info cardinfo-notmfa" id="btn-notmfa-${method.id}">Info</button>
                //             </div>
                //         </div>
                //     `;
                //     // Adjusting the trigger selector to target the unique button ID
                //     setModal(`#btn-notmfa-${method.id}`, modalContent, modalId);
                // } else {
                //     const modalId = `modal-ismfa-${method.id}`; // Unique ID for the modal
                //     card = `
                //         <div class="card my-2">
                //             <div class="card-body">
                //                 <h5 class="card-title">${method['@odata.type']}</h5>
                //                 <p class="card-text">ID: ${method.id}</p>
                //                 <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
                //                 <button class="btn btn-danger btn-ismfa">Remove</button>
                //                 <button class="btn btn-info cardinfo-ismfa" id="btn-ismfa-${method.id}">Info</button>
                //             </div>
                //         </div>
                //     `;
                //     // Setting the trigger selector to the unique ID of the button
                //     setModal(`#btn-ismfa-${method.id}`, modalContent, modalId);
                // }
                // let card;
                // if (method['@odata.type'] === '#microsoft.graph.passwordAuthenticationMethod') {
                //     card = `
                //     <div class="card my-2">
                //         <div class="card-body">
                //             <h5 class="card-title">${method['@odata.type']}</h5>
                //             <p class="card-text">ID: ${method.id}</p>
                //             <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
                //             <button class="btn btn-danger disabled">Remove</button>
                //             <button class="btn btn-info cardinfo-password-danger">Info</button>
                //         </div>
                //     </div>
                // `;
                // setModal('.cardinfo-ismfa', 'hello world cardinfo-password-danger');
                // }
                // else if (method['@odata.type'] !== '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
                //     card = `
                //     <div class="card my-2">
                //         <div class="card-body">
                //             <h5 class="card-title">${method['@odata.type']}</h5>
                //             <p class="card-text">ID: ${method.id}</p>
                //             <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
                //             <button class="btn btn-danger disabled">Remove</button>
                //             <button class="btn btn-info cardinfo-not-mfa">Info</button>
                //         </div>
                //     </div>
                // `;
                // setModal('.cardinfo-not-mfa', 'hello world cardinfo-not-mfa');
                // } else {
                //     card = `
                //     <div class="card my-2">
                //         <div class="card-body">
                //             <h5 class="card-title">${method['@odata.type']}</h5>
                //             <p class="card-text">ID: ${method.id}</p>
                //             <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
                //             <button class="btn btn-danger btn-ismfa">Remove</button>
                //             <button class="btn btn-info cardinfo-ismfa">Info</button>
                //         </div>
                //     </div>
                // `;
                //     setModal('.cardinfo-ismfa', 'hello world cardinfo-ismfa');
                // }

                // container.append(card);

            });
            // container.append(methodDiv);


            // convert to json
            // userAuthenticationMethods = JSON.parse(userAuthenticationMethods);


        } catch (error) {
            console.error('Error:', error);

            // Optionally, show an error message to the user
        } finally {
            // Hide the spinner and enable the button
            spinner.hide();
            button.prop('disabled', false);
            
            
            // console.log('User Info:', userAuthenticationMethods);



        }
    });
});













































// document.addEventListener('DOMContentLoaded', function () {
//     const form = document.querySelector('form');

//     form.addEventListener('submit', function (e) {
//         e.preventDefault(); // Prevent the default form submission
//         const formData = new FormData(form);
//         fetch(form.action, {
//             method: 'POST',
//             body: formData,
//         })
//         .then(response => response.json())
//         .then(data => {
//             updateSessionStorage(data);
//         })
//         .then(() => {
//             updateAuthenticationMethods();
//         })
//         .then(() => {
//             console.log('Form submitted');
//         })
//         .catch(error => console.error('Error:', error));
//     });
// });

// function updateSessionStorage(data) {
//     // save the data to session storage    
//     sessionStorage.setItem('userPrincipalObj', JSON.stringify(data));    
// }





// function updateAuthenticationMethods() {

//     // get session storage data
//     const userPrincipalObj = JSON.parse(sessionStorage.getItem('userPrincipalObj'));
//     const authenticationMethods = JSON.parse(sessionStorage.getItem('userPrincipalObj')).authentication_methods[0];
//     const container = document.querySelector('.container'); // Assuming you want to append the list here
    
//     // Start building HTML content for userPrincipalObj
    
//     let htmlContent = '<div class="user-principal-info">';
//     let elementInfo = document.querySelector('.user-principal-info');
//     if (elementInfo) {
//         elementInfo.remove();
//     }
//     const fields = ['displayName', 'givenName', 'id', 'jobTitle', 'mail', 'mobilePhone', 'officeLocation', 'surname', 'userPrincipalName'];

//     for (const field of fields) {
//         const value = userPrincipalObj[field];
//         if (value !== undefined) {
//             // Handle array values differently to concatenate their contents
//             if (Array.isArray(value)) {
//                 htmlContent += `<div><strong>${field}:</strong> ${value.join(', ')}</div>`;
//             } else {
//                 htmlContent += `<div><strong>${field}:</strong> ${value}</div>`;
//             }
//         }
//     }
//     htmlContent += '</div>'; // Close the user principal info div

//     // Continue with building HTML content for authentication methods
//     htmlContent += '<div class="auth-methods-list">';
//     let elementAuth = document.querySelector('.auth-methods-list');
//     if (elementAuth) {
//         elementAuth.remove();
//     }
//     authenticationMethods.value.forEach(method => {
//         let methodDiv = '<div class="auth-method my-4">';
//         for (const [key, value] of Object.entries(method)) {
//             // if (key !== '@odata.type') { // Skip the @odata.type property
//                 methodDiv += `<span><strong>${key}:</strong> ${value}</span><br>`;
//             // }
//         }

//         // only add button if the @odata.type property contains '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod'
//         if (method['@odata.type'] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
//             // methodDiv += `<button class="btn btn-danger remove-btn" data-method-id="${method.id}">Remove</button>`;
//             methodDiv += `<button class="btn btn-danger remove-btn" data-method-id="${method.id}" data-bs-toggle="modal" data-bs-target="#deleteConfirmationModal">Remove</button>`;

//         } else {
//             methodDiv += `<button type="button" class="btn btn-info" data-bs-toggle="modal" data-bs-target="#infoModal">Info</button>`;
//         }

//         methodDiv += '</div>';
//         htmlContent += methodDiv;
//     });
//     htmlContent += '</div>'; // Close the auth methods list div

//     // container.innerHTML += htmlContent; // Replace the container's content
//     container.insertAdjacentHTML('beforeend', htmlContent); // Append the new HTML
// }




// document.getElementById('confirmDelete').addEventListener('click', function() {
//     // const methodId = window.methodIdToDelete; // The ID captured when the remove button is clicked
//     // const csrftoken = getCookie('csrftoken'); // Function to get CSRF token from cookies


//     const authentication_id = window.methodIdToDelete; // The ID captured when the remove button is clicked
//     const user_principal_id = JSON.parse(sessionStorage.getItem('userPrincipalObj')).id;
//     const csrftoken = getCookie('csrftoken'); // Function to get CSRF token from cookies
    
    

//     // const deleteUrl = `${deleteAuthMethodUrlPattern}${authentication_id}/`; // Assuming methodId is available
//     // const deleteUrl = `/app-main/myview/delete-authentication-method/${user_principal_id}/${authentication_id}/`; // Assuming methodId is available
//     // const deleteUrl = `/myview/mfa-reset/user/${user_principal_id}/delete-authentication/${authentication_id}/`;
//     //                         mfa-reset/user/<str:user_principal_id>/delete-authentication/<str:authentication_id>/

//     const protocol = window.location.protocol;
//     const host = window.location.host;
//     const path = `/myview/mfa-reset/user/${user_principal_id}/delete-authentication/${authentication_id}/`;
//     const deleteUrl = `${protocol}//${host}${path}`;
        

//     fetch(deleteUrl, {
//         method: 'DELETE',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': csrftoken,
//         },
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//     })
//     .then(() => {
//         // updateSessionStorage();
//         updateAuthenticationMethods();
//         displayNotification('The authentication method was successfully deleted.', 'success');

//        // Programmatically hide the modal after successful deletion
//        const deleteConfirmationModal = document.getElementById('deleteConfirmationModal');
//        const bootstrapModal = bootstrap.Modal.getInstance(deleteConfirmationModal);
//        bootstrapModal.hide();
//     })
//     .catch(error => {
//         console.error('There was a problem with the delete request:', error);
//         displayNotification('Error deleting the authentication method.', 'error');
//     });
// });






















// // To capture the method ID before showing the modal
// document.addEventListener('click', function(e) {
//     if (e.target.classList.contains('remove-btn')) {
//         window.methodIdToDelete = e.target.getAttribute('data-method-id'); // Store method ID globally
//     }
// });








































