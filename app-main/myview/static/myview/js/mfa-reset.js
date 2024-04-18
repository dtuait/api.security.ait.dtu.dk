console.log('MFA Reset JS loaded');





async function getUserAuthenticationMethods(userEmail) {
    const url = `/graph/v1.0/list/${encodeURIComponent(userEmail)}/authentication-methods`;

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
    const url = `/graph/v1.0/get-user/${encodeURIComponent(userEmail)}`;
  
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
    const url = `/graph/v1.0/users/${encodeURIComponent(userEmail)}/authentication-methods/${authID}`;

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
        
        // Card is being generated here!
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


