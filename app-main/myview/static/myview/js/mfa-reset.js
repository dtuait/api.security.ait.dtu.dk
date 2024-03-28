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


async function deleteAuthenticationMethod(userEmail, authID) {
    const url = `/v1.0/graph/users/${encodeURIComponent(userEmail)}/authentication-methods/${authID}`;

    let response;
    try {
        const headers = {
            'accept': 'application/json'
        };

        response = await restAjax('DELETE', url, headers);
        // const response = {'status': 204}
        // Check for a 204 status code specifically
        if (response.status === 204) {
            console.log('Authentication Method Deleted Successfully');
        } else {
            console.log('Unexpected response:', response);
            throw new Error('Unexpected response:', response);
        }

        // Since no content is expected, you might not need to return the response
        // But you can return the status for confirmation or further checks
    } catch (error) {
        console.error('Error deleting authentication method:', error);
        
    }
    finally
    {
        return response;
    }
}
  

// Example usage
// result = getUserInfo('vicre-test01@dtudk.onmicrosoft.com');





















////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
// Descriptive programming

async function validateUserEmail() {
    const userEmail = $('#id_username').val();
    if (!userEmail) {
        throw new Error('User email is required');
    }
    return userEmail;
}

async function fetchAndDisplayUserAuthenticationMethods(userEmail) {
    const userAuthenticationMethods = await getUserAuthenticationMethods(userEmail);



    const container = $('#dataContainer');
    container.empty();
    userAuthenticationMethods.data.value.forEach(authenticationMethod => {
        displayAuthenticationMethod(container, authenticationMethod, userEmail);
    });
}

function displayAuthenticationMethod(container, authenticationMethod, userEmail) {
    const {formattedDate, buttonClassSuffix, enabledOrDisabled, modalOptions} = prepareMethodDetails(authenticationMethod);
    const card = constructAuthenticationMethodCard(authenticationMethod, formattedDate, buttonClassSuffix, enabledOrDisabled);
    container.append(card.card);

    // Set the modal for the info button
    setModal(`#${card.infoButtonId}`, `info-${card.modalId}`, modalOptions); // Set the modal for the info button    
    // Define the options for the delete confirmation modal
    const deleteModalOptions = {
        title: "Confirm Deletion",
        body: "Are you sure you want to delete this authentication method?",
        footer: `
        <button type="button" class="btn btn-danger" id="deleteConfirmButton">Yes, Delete it</button>
        <button type="button" class="btn btn-success" data-bs-dismiss="modal">No, Cancel</button>
        `,
        'eventListeners': [
            {
                selector: '#deleteConfirmButton',
                event: 'click',
                handler: async function() {
                    // log
                    console.log('Delete button clicked for user:', userEmail, 'and method:', authenticationMethod.id);
                    let response;
                    try {
                    
                    response = await deleteAuthenticationMethod(userEmail, authenticationMethod.id);
                    console.log('Response:', response);



                    } catch (error) {
                    console.error('Error deleting authentication method:', error);
                    // Optionally, show an error message to the user
                    } finally {
                    // Programmatically hide the modal after successful deletion
                    const deleteConfirmationModal = document.getElementById(`delete-${card.deleteButtonId}`);
                    const bootstrapModal = bootstrap.Modal.getInstance(deleteConfirmationModal);
                    bootstrapModal.hide();


                    const userLookup = await handleUserLookup();
                    
                    if (response.status === 204 && userLookup) {
                        displayNotification('The authentication method was successfully deleted.', 'success');
                    } else {
                        displayNotification('An unknown error occurred.', 'warning');
                    }


                    }

                }
              }
        ]
    };

    // help me create a dialog model that has a text 
    // Are you sure you want to delete this authentication method?
    // Red Button: Yes, Delete it
    // Green Button: No, Cancel
    // log json deleteModalOptions
    setModal(`#${card.deleteButtonId}`, `delete-${card.deleteButtonId}`, deleteModalOptions); // Set the modal for the delete button
   
   
   
}

function prepareMethodDetails(method) {
    const date = new Date(method.createdDateTime);
    const formattedDate = date.toLocaleString('en-GB', { timeZone: 'UTC' });
    let {buttonClassSuffix, enabledOrDisabled, modalOptions} = determineMethodVariables(method);
    return {formattedDate, buttonClassSuffix, enabledOrDisabled, modalOptions};
}

function determineMethodVariables(method) {
    let buttonClassSuffix, enabledOrDisabled, modalOptions = {};
    const protocol = window.location.protocol;
    const server = window.location.hostname;
    const port = window.location.port;

    if (method['@odata.type'] === '#microsoft.graph.passwordAuthenticationMethod') {
        buttonClassSuffix = 'password';
        enabledOrDisabled = 'disabled';
    } else if (method['@odata.type'] !== '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
        buttonClassSuffix = 'notmfa';
        enabledOrDisabled = 'disabled';
    } else {
        buttonClassSuffix = 'ismfa';
        enabledOrDisabled = '';
    }
    modalOptions = assignModalOptions(protocol, server, port, buttonClassSuffix);
    return {buttonClassSuffix, enabledOrDisabled, modalOptions};
}

function assignModalOptions(protocol, server, port, buttonClassSuffix) {
    let modalOptions = { title: '', body: '' };
    if (buttonClassSuffix === 'password' || buttonClassSuffix === 'notmfa') {
        modalOptions.title = `${buttonClassSuffix === 'password' ? 'Password' : 'Not MFA'} Authentication Method`;
        modalOptions.body = `This authentication method is disabled because it is not an MFA method. If you want to DELETE it, you can do it via the API:<br><a href="${protocol}//${server}:${port}/myview/swagger/">${protocol}//${server}:${port}/myview/swagger/</a>`;
    } else {
        modalOptions.title = 'MFA Method';
        modalOptions.body = 'This authentication method is MFA.';
    }
    return modalOptions;
}

function constructAuthenticationMethodCard(method, formattedDate, buttonClassSuffix, enabledOrDisabled) {
    const infoButtonId = `info-btn-${buttonClassSuffix}-${method.id}`;
    const deleteButtonId = `delete-btn-${buttonClassSuffix}-${method.id}`;
    const modalId = `modal-${buttonClassSuffix}-${method.id}`;

    // if formattded date is 1970 then it is N/A
    let cardObj  =  {
        'infoButtonId': infoButtonId,
        'deleteButtonId': deleteButtonId,
        'modalId': modalId,
        'card': ''
        // `
        //     <div class="card my-2">
        //         <div class="card-body">
        //             <h5 class="card-title">${method['@odata.type']}</h5>
        //             <p class="card-text">ID: ${method.id}</p>
        //             <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
        //             <button class="btn btn-danger ${enabledOrDisabled}" id="${deleteButtonId}">Remove</button>
        //             <button class="btn btn-info cardinfo-${buttonClassSuffix}" id="${infoButtonId}">Info</button>
        //         </div>
        //     </div>
        // `
        }

        cardObj.card += `
            <div class="card my-2">
                <div class="card-body">
                    <h5 class="card-title">${method['@odata.type']}</h5>
        `;

        Object.entries(method).forEach(([key, value]) => {
            if (key !== '@odata.type') {
                cardObj.card += `<p class="card-text">${key}: ${value}</p>`;
            }
            else if (key === 'createdDateTime') {
                cardObj.card += `<p class="card-text">${key}: ${formattedDate || 'N/A'}</p>`;
            }
        });

        cardObj.card += `
                    <button class="btn btn-danger ${enabledOrDisabled}" id="${deleteButtonId}">Remove</button>
                    <button class="btn btn-info cardinfo-${buttonClassSuffix}" id="${infoButtonId}">Info</button>
                </div>
            </div>
        `

    

    return cardObj;
}





async function handleUserLookup() {
    const button = $('#mfa-user-lookup-submit-btn');
    const spinner = $('#loadingSpinner');

    // Initiate UI feedback for processing
    spinner.show();
    button.prop('disabled', true);

    try {
        // Validate and retrieve the user email
        
        userEmail = await validateUserEmail();
        
        // Fetch and display authentication methods for the user
        await fetchAndDisplayUserAuthenticationMethods(userEmail);
    } catch (error) {
        // Handle any errors that occur during the fetch and display process
        console.error('Error:', error);
        return false;
        // Optionally, you could display an error message to the user here
    } finally {
        // Regardless of the outcome, reset the UI feedback
        spinner.hide();
        button.prop('disabled', false);
        return true;
    }
}

$('#mfa-user-lookup-submit-btn').on('click', handleUserLookup);



// $('#mfa-user-lookup-submit-btn').on('click', async function () {
//     const button = $(this);
//     const spinner = $('#loadingSpinner');

//     // Initiate UI feedback for processing
//     spinner.show();
//     button.prop('disabled', true);

//     try {
//         // Validate and retrieve the user email
//         const userEmail = await validateUserEmail();
//         // Fetch and display authentication methods for the user
//         await fetchAndDisplayUserAuthenticationMethods(userEmail);


//     } catch (error) {
//         // Handle any errors that occur during the fetch and display process
//         console.error('Error:', error);
//         // Optionally, you could display an error message to the user here
//     } finally {
//         // Regardless of the outcome, reset the UI feedback
//         spinner.hide();
//         button.prop('disabled', false);
//     }
// });

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	









// $('#mfa-user-lookup-submit-btn').on('click', async function () {
//     const button = $(this);
//     const spinner = $('#loadingSpinner');

//     // Show the spinner and disable the button
//     spinner.show();
//     button.prop('disabled', true);


//     let userAuthenticationMethods;
//     try {


//         const userEmail = $('#id_username').val();
//         if (!userEmail) {
//             return;
//         }

//         const userInfo = await getUserInfo(userEmail);
//         userAuthenticationMethods = await getUserAuthenticationMethods(userEmail);

//         const container = $('#dataContainer');
//         container.empty();
//         userAuthenticationMethods.value.forEach(method => {
            
//             // '2024-03-12T13:25:21Z' should be converted into MM:HH dd-mm-yyyy
//             const date = new Date(method.createdDateTime);
//             const formattedDate = date.toLocaleString('en-GB', { timeZone: 'UTC' });
//             console.log(formattedDate);


//             const protocol = window.location.protocol;
//             const server = window.location.hostname;
//             const port = window.location.port;


//             // Variables that may change based on conditions
//             let buttonClassSuffix;
//             let enabledOrDisabled;
//             let modalOptions = {}


//             // Determine the variables based on the method type
//             if (method['@odata.type'] === '#microsoft.graph.passwordAuthenticationMethod') {
//                 buttonClassSuffix = 'password';
//                 modalOptions.title = 'Password Authentication Method';
//                 modalOptions.body = `
//                 This authentication method is disabled because it is not an MFA method. If you want to DELETE it, you can do it via the API:<br>
//                 <a href="${protocol}//${server}:${port}/myview/swagger/">${protocol}//${server}:${port}/myview/swagger/</a>
//                 `;
//                 enabledOrDisabled = 'disabled';
//             } else if (method['@odata.type'] !== '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
//                 buttonClassSuffix = 'notmfa';
//                 modalOptions.title = 'Not MFA Method';

//                 modalOptions.body = `
//                 This authentication method is disabled because it is not an MFA method. If you want to DELETE it, you can do it via the API:<br>
//                 <a href="${protocol}//${server}:${port}/myview/swagger/">${protocol}//${server}:${port}/myview/swagger/</a>
//                 `;
//                 enabledOrDisabled = 'disabled';
//             } else {
//                 buttonClassSuffix = 'ismfa';
//                 modalOptions.title = 'MFA Method';
//                 modalOptions.body = `
//                 This is authentication method is MFA.
//             `;
//                 enabledOrDisabled = '';
//             }

//             // Now, construct the unique IDs based on the determined variables
//             const buttonId = `btn-${buttonClassSuffix}-${method.id}`;
//             const modalId = `modal-${buttonClassSuffix}-${method.id}`;
            

//             // Construct the card with dynamic parts
//             let card = `
//                 <div class="card my-2">
//                     <div class="card-body">
//                         <h5 class="card-title">${method['@odata.type']}</h5>
//                         <p class="card-text">ID: ${method.id}</p>
//                         <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
//                         <button class="btn btn-danger ${enabledOrDisabled}">Remove</button>
//                         <button class="btn btn-info cardinfo-${buttonClassSuffix}" id="${buttonId}">Info</button>
//                     </div>
//                 </div>
//             `;

//             container.append(card);
//             setModal(`#${buttonId}`, modalId, modalOptions);
            

//         });



//     } catch (error) {
//         console.error('Error:', error);

//         // Optionally, show an error message to the user
//     } finally {
//         // Hide the spinner and enable the button
//         spinner.hide();
//         button.prop('disabled', false);
    
//     }
// });













































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








































