console.log('MFA Reset JS loaded');







class AppUtils {
    constructor() {
        if (!AppUtils.instance) {
            AppUtils.instance = this;
        }
        return AppUtils.instance;
    }


    printHelloWorld() {
        console.log('Hello World');
    }


    async validateUserPrincipalName(userPrincipalName) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;  // Regular expression for validating email

        // Check if the userPrincipalName field is empty
        if (!userPrincipalName) {
            throw new Error('userPrincipalName field cannot be empty.');  // Throw an error with a specific message
        }

        // Check if the input is a valid email
        if (!emailRegex.test(userPrincipalName)) {
            throw new Error('Invalid userPrincipalName format.');  // Throw an error with a specific message
        }

        return true;
    }


    async getUserAuthenticationMethods(app) {

        const userPrincipalName = app.uiBinder.userPrincipalName.val();  // Get the userPrincipalName

        const url = `/graph/v1.0/list/${encodeURIComponent(userPrincipalName)}/authentication-methods`;

        try {

            const response = await app.baseAppUtils.restAjax('GET', url);

            if (response.status !== 200) {
                throw new Error(`getUserAuthenticationMethods \t ${response.data.message}, ${response.status}`)
            }

            return response;
        } catch (error) {
            throw error;
        }
    }


    prepareMethodDetails(method) {
        const date = new Date(method.createdDateTime);
        const formattedDate = date.toLocaleString('en-GB', { timeZone: 'UTC' });
        let { buttonClassSuffix, enabledOrDisabled, modalOptions } = this.determineMethodVariables(method);
        return { formattedDate, buttonClassSuffix, enabledOrDisabled, modalOptions };
    }

    determineMethodVariables(method) {
        let buttonClassSuffix, enabledOrDisabled, modalOptions = {};
        const protocol = window.location.protocol;
        const server = window.location.hostname;
        const port = window.location.port;
    
        if (method['@odata.type'] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
            buttonClassSuffix = 'ismfa';
            enabledOrDisabled = '';
        } else if (method['@odata.type'] === '#microsoft.graph.phoneAuthenticationMethod') {
            buttonClassSuffix = 'ismfa';
            enabledOrDisabled = '';
        } else {
            buttonClassSuffix = 'notmfa';
            enabledOrDisabled = 'disabled';
        }
        modalOptions = this.assignModalOptions(protocol, server, port, buttonClassSuffix);
        return { buttonClassSuffix, enabledOrDisabled, modalOptions };
    }

    assignModalOptions(protocol, server, port, buttonClassSuffix) {
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

    async fetchAndDisplayUserAuthenticationMethods(app) {

        try {

            const userPrincipalName = app.uiBinder.userPrincipalName.val();  // Get the userPrincipalName
            const cardsContainer = app.uiBinder.cardsContainer;  // Get the cards container

            const userAuthenticationMethods = await app.appUtils.getUserAuthenticationMethods(app);

            // clear the card container
            app.uiBinder.cardsContainer.empty();
            userAuthenticationMethods.data.value.forEach(authenticationMethod => {
                this.displayAuthenticationMethod(app, authenticationMethod);
            });

        } catch (error) {
            throw error;
        }


    }



    displayAuthenticationMethod(app, authenticationMethod) {

        try {
            const userPrincipalName = app.uiBinder.userPrincipalName.val();  // Get the userPrincipalName
            const { formattedDate, buttonClassSuffix, enabledOrDisabled, modalOptions } = this.prepareMethodDetails(authenticationMethod);

            const card = this.constructAuthenticationMethodCard(authenticationMethod, formattedDate, buttonClassSuffix, enabledOrDisabled);
            app.uiBinder.cardsContainer.append(card.card);

            // Set the modal for the info button
            app.baseAppUtils.setModal(`#${card.infoButtonId}`, `info-${card.modalId}`, modalOptions); // Set the modal for the info button    
            // Define the options for the delete confirmation modal
            const deleteModalOptions = {
                title: "Confirm Deletion",
                body: "Are you sure you want to delete this authentication method?",
                footer: `
                <button type="button" class="btn btn-danger" id="deleteConfirmButton">Yes, Delete it</button>
                <button type="button" class="btn btn-info data-bs-dismiss="modal">No, Cancel</button>
                `,
                'eventListeners': [
                    {
                        selector: '#deleteConfirmButton',
                        event: 'click',
                        handler: async function () {

                            let response;
                            try {

                                response = await deleteAuthenticationMethod(userPrincipalName, authenticationMethod.id);

                                // Programmatically hide the modal after successful deletion
                                const deleteConfirmationModal = document.getElementById(`delete-${card.deleteButtonId}`);
                                const bootstrapModal = bootstrap.Modal.getInstance(deleteConfirmationModal);
                                bootstrapModal.hide();


                                const userLookup = await handleUserLookup();

                                displayNotification('The authentication method was successfully deleted.', 'success');


                            } catch (error) {
                                // Display specific error messages
                                notificationsContainer.empty();  // Clear any existing notifications
                                let errorMessage = 'Failed to delete authentication method details: ' + (error.message || 'Unknown error');
                                notificationsContainer.append(`
                                    <div class="alert alert-danger" role="alert">
                                        ${errorMessage}
                                    </div>
                                `);
                                console.error('Error:', error);  // Log error for debugging
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
            app.baseAppUtils.setModal(`#${card.deleteButtonId}`, `delete-${card.deleteButtonId}`, deleteModalOptions); // Set the modal for the delete button


        } catch (error) {
            throw error;
        }


    }




    constructAuthenticationMethodCard(method, formattedDate, buttonClassSuffix, enabledOrDisabled) {
        const infoButtonId = `info-btn-${buttonClassSuffix}-${method.id}`;
        const deleteButtonId = `delete-btn-${buttonClassSuffix}-${method.id}`;
        const modalId = `modal-${buttonClassSuffix}-${method.id}`;
    
        // if formattded date is 1970 then it is N/A
        let cardObj = {
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

    static getInstance() {
        if (!AppUtils.instance) {
            AppUtils.instance = new AppUtils();
        }
        return AppUtils.instance;
    }
}






class App {
    constructor(uiBinder = UIBinder.getInstance(), baseUIBinder = BaseUIBinder.getInstance(), appUtils = AppUtils.getInstance(), baseAppUtils = BaseAppUtils.getInstance()) {

        if (!App.instance) {
            this.uiBinder = uiBinder;
            this.baseUIBinder = baseUIBinder;
            this.appUtils = appUtils;
            this.baseAppUtils = baseAppUtils;
            this._setBindings();
            App.instance = this;
        }

        return App.instance;
    }

    _setBindings() {

        // Set binding for user lookup form submission
        this.uiBinder.mfaUserLookupSubmitBtn.on('click', this.handleUserLookup.bind(this));
    }

    async handleUserLookup(event) {
        event.preventDefault();

        // this.baseUIBinder.displayNotification("Hello World", "alert-info");
        this.uiBinder.spinner.show();
        this.uiBinder.mfaUserLookupSubmitBtn.prop('disabled', true);

        try {

            await this.appUtils.validateUserPrincipalName(this.uiBinder.userPrincipalName.val());

            await this.appUtils.fetchAndDisplayUserAuthenticationMethods(this)

            this.baseUIBinder.displayNotification('User lookup successful', 'alert-info' , 5000);

        } catch (error) {
            this.baseUIBinder.displayNotification(`${error} `, 'alert-danger');
            console.log(error);
        } finally {
            this.uiBinder.spinner.hide();
            this.uiBinder.mfaUserLookupSubmitBtn.prop('disabled', false);
        }



    }

    static getInstance(uiBinder = UIBinder.getInstance(), baseUIBinder = BaseUIBinder.getInstance(), appUtils = AppUtils.getInstance(), baseAppUtils = BaseAppUtils.getInstance()) {
        if (!App.instance) {
            App.instance = new App(uiBinder, baseUIBinder, appUtils, baseAppUtils);
        }
        return App.instance;
    }
}







class UIBinder {
    constructor() {

        if (!UIBinder.instance) {

            this.mfaUserLookupSubmitBtn = $('#mfa-user-lookup-submit-btn');
            this.spinner = $('#loadingSpinner');
            this.userPrincipalName = $('#id-userprincipalname');
            this.cardsContainer = $('#cards-container');
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











document.addEventListener('DOMContentLoaded', function () {

    const app = App.getInstance();


});










