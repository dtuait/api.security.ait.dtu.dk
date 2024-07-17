console.log('MFA Reset JS loaded');


// class UIManager extends BaseUIManager {
//     constructor() {


//         super(); // Call the constructor of the BaseUIManager
//         // Additional initialization for mfa-reset page
//         this.mfaUserLookupSubmitBtn = $('#mfa-user-lookup-submit-btn');
//         this.button = $('#mfa-user-lookup-submit-btn');
//         this.spinner = $('#loadingSpinner');
//         this.userPrincipalName = $('#id-userprincipalname');
//         this.cardsContainer = $('#cards-container');

//         // Initialize the MFA User Lookup Submit button
//         this._initializeMFAUserLookupSubmitBtn();
//     }

//     _initializeMFAUserLookupSubmitBtn() {
//         // Specific logic for the reset form
//         this.mfaUserLookupSubmitBtn.on('submit', this.handleResetFormSubmit.bind(this));
//     }

//     handleResetFormSubmit(event) {
//         event.preventDefault();
//         // Implementation for handling form submit
//         console.log('Reset form submitted');
//     }





// }






class AppUtils {
    constructor() {
        if (!AppUtils.instance) {
            AppUtils.instance = this;
        }
        return AppUtils.instance;
    }


    static getInstance() {
        if (!AppUtils.instance) {
            AppUtils.instance = new AppUtils();
        }
        return AppUtils.instance;
    }
}






class UIManager {
    constructor(baseUIManager = BaseUIManager.getInstance(), appUtils = AppUtils.getInstance()) {

        if (!UIManager.instance) {
            this.baseUIManager = baseUIManager;
            this.mfaUserLookupSubmitBtn = $('#mfa-user-lookup-submit-btn');
            this.spinner = $('#loadingSpinner');
            this.userPrincipalName = $('#id-userprincipalname');
            this.cardsContainer = $('#cards-container');
            this._setBindings();
            UIManager.instance = this;
        }

        return UIManager.instance;
    }

    _setBindings() {

        // Set binding for user lookup form submission
        this.mfaUserLookupSubmitBtn.on('click', this.handleUserLookup.bind(this));
    }

    handleUserLookup(event) {
        event.preventDefault();
        console.log('Reset form submitted');
        // Here you can access BaseUIManager's methods if needed
        // For example: this.baseUIManager.someMethod();
    }

    static getInstance(baseUIManager = BaseUIManager.getInstance()) {
        if (!UIManager.instance) {
            UIManager.instance = new UIManager(baseUIManager);
        }
        return UIManager.instance;
    }
}







class UIBinder {
    constructor() {

        if (!UIBinder.instance) {

            this.mfaUserLookupSubmitBtn = $('#mfa-user-lookup-submit-btn');
            this.spinner = $('#loadingSpinner');
            this.userPrincipalName = $('#id-userprincipalname');
            this.cardsContainer = $('#cards-container');
            this._setBindings();
            UIBinder.instance = this;
        }

        return UIBinder.instance;
    }


 

    static getInstance() {
        if (!UIBinder.instance) {
            UIBinder.instance = new UIBinder();
        }
        return UIBinder.instance;
    }
}








// async function getUserAuthenticationMethods(userPrincipalName) {
//     const url = `/graph/v1.0/list/${encodeURIComponent(userPrincipalName)}/authentication-methods`;

//     try {

//         const response = await restAjax('GET', url);

//         if (response.status !== 200) {
//             throw new Error(`getUserAuthenticationMethods \t ${response.data.message}, ${response.status}`)
//         }

//         return response;
//     } catch (error) {
//         console.error('Error fetching user authentication methods:', error);
//         throw error; // Allowing the caller to handle errors
//     }
// }


// async function getUserInfo(userEmail) {
//     const url = `/graph/v1.0/get-user/${encodeURIComponent(userEmail)}`;

//     try {
//         const response = await restAjax('GET', url);
//         console.log('User Info:', response);
//         return response;
//     } catch (error) {
//         console.error('Error fetching user info:', error);
//         throw error; // Allowing the caller to handle errors
//     }
// }


// async function deleteAuthenticationMethod(userEmail, authID) {
//     const url = `/graph/v1.0/users/${encodeURIComponent(userEmail)}/authentication-methods/${authID}`;

//     let response;
//     try {
//         const headers = {
//             'accept': 'application/json'
//         };

//         response = await restAjax('DELETE', url, headers);
//         // const response = {'status': 204}
//         // Check for a 204 status code specifically

//         if (response.status !== 204) {
//             throw new Error(`deleteAuthenticationMethod \t ${response.data.message}, ${response.status}`)
//         }

//         return response;

//         // Since no content is expected, you might not need to return the response
//         // But you can return the status for confirmation or further checks
//     } catch (error) {
//         throw error; // Allowing the caller to handle errors
//     }
// }


// // Example usage
// // result = getUserInfo('vicre-test01@dtudk.onmicrosoft.com');





















// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////	
// // Descriptive programming

// async function validateUserPrincipalName(myuiManager) {
//     const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;  // Regular expression for validating email

//     const userPrincipalName = myuiManager.userPrincipalName.val();  // Get the userPrincipalName value

//     // Check if the userPrincipalName field is empty
//     if (!userPrincipalName) {
//         throw new Error('userPrincipalName field cannot be empty.');  // Throw an error with a specific message
//     }

//     // Check if the input is a valid email
//     if (!emailRegex.test(userPrincipalName)) {
//         throw new Error('Invalid userPrincipalName format.');  // Throw an error with a specific message
//     }

//     return true;  // Return true if the userPrincipalName is valid
// }


// async function fetchAndDisplayUserAuthenticationMethods(myuiManager) {
//     const userPrincipalName = myuiManager.userPrincipalName.val();  // Get the userPrincipalName value
//     const cardsContainer = myuiManager.cardsContainer;  // Get the cards container
//     const userAuthenticationMethods = await getUserAuthenticationMethods(userPrincipalName);



//     cardsContainer.empty();  // Clear the cards container
//     userAuthenticationMethods.data.value.forEach(authenticationMethod => {
//         displayAuthenticationMethod(cardsContainer, authenticationMethod, userPrincipalName);
//     });
// }

// function displayAuthenticationMethod(container, authenticationMethod, userPrincipalName) {
//     const { formattedDate, buttonClassSuffix, enabledOrDisabled, modalOptions } = prepareMethodDetails(authenticationMethod);
//     const card = constructAuthenticationMethodCard(authenticationMethod, formattedDate, buttonClassSuffix, enabledOrDisabled);
//     container.append(card.card);

//     // Set the modal for the info button
//     setModal(`#${card.infoButtonId}`, `info-${card.modalId}`, modalOptions); // Set the modal for the info button    
//     // Define the options for the delete confirmation modal
//     const deleteModalOptions = {
//         title: "Confirm Deletion",
//         body: "Are you sure you want to delete this authentication method?",
//         footer: `
//         <button type="button" class="btn btn-danger" id="deleteConfirmButton">Yes, Delete it</button>
//         <button type="button" class="btn btn-success" data-bs-dismiss="modal">No, Cancel</button>
//         `,
//         'eventListeners': [
//             {
//                 selector: '#deleteConfirmButton',
//                 event: 'click',
//                 handler: async function () {

//                     let response;
//                     try {

//                         response = await deleteAuthenticationMethod(userPrincipalName, authenticationMethod.id);

//                         // Programmatically hide the modal after successful deletion
//                         const deleteConfirmationModal = document.getElementById(`delete-${card.deleteButtonId}`);
//                         const bootstrapModal = bootstrap.Modal.getInstance(deleteConfirmationModal);
//                         bootstrapModal.hide();


//                         const userLookup = await handleUserLookup();

//                         displayNotification('The authentication method was successfully deleted.', 'success');


//                     } catch (error) {
//                         // Display specific error messages
//                         notificationsContainer.empty();  // Clear any existing notifications
//                         let errorMessage = 'Failed to delete authentication method details: ' + (error.message || 'Unknown error');
//                         notificationsContainer.append(`
//                             <div class="alert alert-danger" role="alert">
//                                 ${errorMessage}
//                             </div>
//                         `);
//                         console.error('Error:', error);  // Log error for debugging
//                     }

//                 }
//             }
//         ]
//     };

//     // help me create a dialog model that has a text 
//     // Are you sure you want to delete this authentication method?
//     // Red Button: Yes, Delete it
//     // Green Button: No, Cancel
//     // log json deleteModalOptions
//     setModal(`#${card.deleteButtonId}`, `delete-${card.deleteButtonId}`, deleteModalOptions); // Set the modal for the delete button



// }

// function prepareMethodDetails(method) {
//     const date = new Date(method.createdDateTime);
//     const formattedDate = date.toLocaleString('en-GB', { timeZone: 'UTC' });
//     let { buttonClassSuffix, enabledOrDisabled, modalOptions } = determineMethodVariables(method);
//     return { formattedDate, buttonClassSuffix, enabledOrDisabled, modalOptions };
// }

// function determineMethodVariables(method) {
//     let buttonClassSuffix, enabledOrDisabled, modalOptions = {};
//     const protocol = window.location.protocol;
//     const server = window.location.hostname;
//     const port = window.location.port;

//     if (method['@odata.type'] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
//         buttonClassSuffix = 'ismfa';
//         enabledOrDisabled = '';
//     } else if (method['@odata.type'] === '#microsoft.graph.phoneAuthenticationMethod') {
//         buttonClassSuffix = 'ismfa';
//         enabledOrDisabled = '';
//     } else {
//         buttonClassSuffix = 'notmfa';
//         enabledOrDisabled = 'disabled';
//     }
//     modalOptions = assignModalOptions(protocol, server, port, buttonClassSuffix);
//     return { buttonClassSuffix, enabledOrDisabled, modalOptions };
// }

// function assignModalOptions(protocol, server, port, buttonClassSuffix) {
//     let modalOptions = { title: '', body: '' };
//     if (buttonClassSuffix === 'password' || buttonClassSuffix === 'notmfa') {
//         modalOptions.title = `${buttonClassSuffix === 'password' ? 'Password' : 'Not MFA'} Authentication Method`;
//         modalOptions.body = `This authentication method is disabled because it is not an MFA method. If you want to DELETE it, you can do it via the API:<br><a href="${protocol}//${server}:${port}/myview/swagger/">${protocol}//${server}:${port}/myview/swagger/</a>`;
//     } else {
//         modalOptions.title = 'MFA Method';
//         modalOptions.body = 'This authentication method is MFA.';
//     }
//     return modalOptions;
// }

// function constructAuthenticationMethodCard(method, formattedDate, buttonClassSuffix, enabledOrDisabled) {
//     const infoButtonId = `info-btn-${buttonClassSuffix}-${method.id}`;
//     const deleteButtonId = `delete-btn-${buttonClassSuffix}-${method.id}`;
//     const modalId = `modal-${buttonClassSuffix}-${method.id}`;

//     // if formattded date is 1970 then it is N/A
//     let cardObj = {
//         'infoButtonId': infoButtonId,
//         'deleteButtonId': deleteButtonId,
//         'modalId': modalId,
//         'card': ''
//         // `
//         //     <div class="card my-2">
//         //         <div class="card-body">
//         //             <h5 class="card-title">${method['@odata.type']}</h5>
//         //             <p class="card-text">ID: ${method.id}</p>
//         //             <p class="card-text">Created: ${formattedDate || 'N/A'}</p>
//         //             <button class="btn btn-danger ${enabledOrDisabled}" id="${deleteButtonId}">Remove</button>
//         //             <button class="btn btn-info cardinfo-${buttonClassSuffix}" id="${infoButtonId}">Info</button>
//         //         </div>
//         //     </div>
//         // `
//     }

//     // Card is being generated here!
//     cardObj.card += `
//             <div class="card my-2">
//                 <div class="card-body">
//                     <h5 class="card-title">${method['@odata.type']}</h5>
//         `;

//     Object.entries(method).forEach(([key, value]) => {
//         if (key !== '@odata.type') {
//             cardObj.card += `<p class="card-text">${key}: ${value}</p>`;
//         }
//         else if (key === 'createdDateTime') {
//             cardObj.card += `<p class="card-text">${key}: ${formattedDate || 'N/A'}</p>`;
//         }
//     });

//     cardObj.card += `
//                     <button class="btn btn-danger ${enabledOrDisabled}" id="${deleteButtonId}">Remove</button>
//                     <button class="btn btn-info cardinfo-${buttonClassSuffix}" id="${infoButtonId}">Info</button>
//                 </div>
//             </div>
//         `

//     return cardObj;
// }





// async function handleUserLookup() {

//     // all the variables needed for the function are defined here
//     const myuiManager = {
//         button: $('#mfa-user-lookup-submit-btn'),
//         spinner: $('#loadingSpinner'),
//         notificationsContainer: $('#notifications-container'),
//         userPrincipalName: $('#id-userprincipalname'),
//         cardsContainer: $('#cards-container')
//     }

//     const button = $('#mfa-user-lookup-submit-btn');
//     const spinner = $('#loadingSpinner');
//     const notificationsContainer = $('#notifications-container');
//     const userPrincipalName = $('#id-userprincipalname').val();



//     notificationsContainer.empty();  // Clear previous notifications
//     spinner.show();  // Show loading indicator
//     button.prop('disabled', true);  // Disable button during processing

//     try {

//         // throws an error if the email is invalid
//         await validateUserPrincipalName(myuiManager);  // Validate email


//         // Fetch and display authentication methods for the user
//         // The rabbit hole goes deep here. But if an error occurs, it will be caught and displayed
//         await fetchAndDisplayUserAuthenticationMethods(myuiManager);

//         // Fetch the user's authentication methods
//         // Assume fetching and validation succeed:
//         notificationsContainer.append(`
//             <div class="alert alert-success" role="alert">
//                 User authentication methods fetched successfully.
//             </div>
//         `);
//     } catch (error) {
//         // Display specific error messages
//         notificationsContainer.empty();  // Clear any existing notifications
//         let errorMessage = 'Failed to fetch user details: ' + (error.message || 'Unknown error');
//         notificationsContainer.append(`
//             <div class="alert alert-danger" role="alert">
//                 ${errorMessage}
//             </div>
//         `);
//         console.error('Error:', error);  // Log error for debugging
//         return false;
//     } finally {
//         // Reset UI elements
//         spinner.hide();  // Hide loading indicator
//         button.prop('disabled', false);  // Enable button
//         return true;
//     }
// }








document.addEventListener('DOMContentLoaded', function () {
    // Initialize the UI manager for mfa-reset page
    // baseUIManager is defiened in base.js
    const baseUIBinder = BaseUIBinder.getInstance(); // Get the instance of BaseUIManager
    const baseAppUtils = BaseAppUtils.getInstance(); // Get the instance of BaseApp
    const appUtils = AppUtils.getInstance(); // Get the instance of App
    const uiManager = UIBinder.getInstance(); // Create an instance of UIManager




    // const uiManager = new UIManager(baseUIManager); // Create an instance of UIManager
    // uiManager.setBindings(); // Set the bindings for the UI elements


    // $('#mfa-user-lookup-submit-btn').on('click', function (event) {
    //     event.preventDefault(); // Prevent the default form submission
    //     handleUserLookup();
    // });



});










