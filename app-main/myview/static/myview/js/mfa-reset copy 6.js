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



            const infoDialogDisplay = app.baseAppUtils.setModal(`#${card.infoButtonId}`, `info-${card.modalId}`, modalOptions); // Set the modal for the info button    


            const deleteConfirmButtonId = `delete-confirm-button`;
            const deleteCancelButtonId = `delete-cancel-button`;
            const deleteModalOptions = {
                title: "Confirm Deletion",
                body: "<p>Are you sure you want to delete this authentication method?</p>",
                footer: `
                <button type="button" class="btn btn-danger" id="${deleteConfirmButtonId}">Yes, Delete it</button>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="${deleteCancelButtonId}">No, Cancel</button>
                `,
                eventListeners: [
                    {
                        selector: `#${deleteConfirmButtonId}`,
                        event: 'click',
                        handler: async function () {
                            try {
                                console.log("deleteConfirmButtonId clicked");
                                await app.appUtils.deleteAuthenticationMethod(app, userPrincipalName, authenticationMethod.id);
                                app.baseUIBinder.displayNotification(`The authentication method was successfully deleted. Refreshes the page in 2 seconds`, 'alert-success');
                                app.appUtils.setUserPrincipalNameQueryParam(userPrincipalName);
                                setTimeout(() => {
                                    location.reload();
                                }, 2000);
            
                            } catch (error) {
                                app.baseUIBinder.displayNotification(`${error} `, 'alert-danger');
                                console.log(error);
                            } finally {
                                deleteDialogDisplay.hide();
                            }
                        }
                    },
                    {
                        selector: `#${deleteCancelButtonId}`,
                        event: 'click',
                        handler: function () {
                            console.log("deleteCancelButtonId clicked");
                        }
                    }
                ]
            };
            const deleteDialogDisplay = app.baseAppUtils.setModal(`#${card.deleteButtonId}`, `delete-${card.deleteButtonId}`, deleteModalOptions);



            // Attach event listeners to the delete confirmation modal buttons
            $(`#${deleteConfirmButtonId}`).on('click', async function () {
                try {
                    app.baseUIBinder.displayNotification(`The authentication method was successfully deleted. Refreshes the page in 5 seconds`, 'alert-success');
                    app.appUtils.setUserPrincipalNameQueryParam(userPrincipalName);
                    setTimeout(() => {
                        location.reload();
                    }, 5000);

                    deleteDialogDisplay.hide();
                } catch (error) {
                    app.baseUIBinder.displayNotification(`${error} `, 'alert-danger');
                    console.log(error);
                } finally {
                    deleteDialogDisplay.hide();
                }
            });


            console.log('deleteCancelButtonId', deleteCancelButtonId);
            console.log($(`#${deleteConfirmButtonId}`));

            $(`#${deleteCancelButtonId}`).on('click', function () {
                console.log("deleteCancelButtonId clicked");
            });


        } catch (error) {
            throw error;
        }


    }


    setUserPrincipalNameQueryParam(userPrincipalName) {
        // Create a URL object based on the current location
        const currentUrl = new URL(window.location);
    
        // Access the URL's search parameters
        const searchParams = currentUrl.searchParams;
    
        // Set or update the userPrincipalName parameter
        searchParams.set('userPrincipalName', userPrincipalName);
    
        // Construct the new URL with the updated search parameters
        const newUrl = `${currentUrl.origin}${currentUrl.pathname}?${searchParams.toString()}`;
    
        // Use history.pushState to change the URL without reloading the page
        window.history.pushState({ path: newUrl }, '', newUrl);
    }


    async deleteAuthenticationMethod(app, userEmail, authID) {
        const url = `/graph/v1.0/users/${encodeURIComponent(userEmail)}/authentication-methods/${authID}`;

        let response;
        try {
            const headers = {
                'accept': 'application/json'
            };

            response = await app.baseAppUtils.restAjax('DELETE', url, headers);
            // const response = {'status': 204}
            // Check for a 204 status code specifically

            if (response.status !== 204) {
                throw new Error(`deleteAuthenticationMethod \t ${response.data.message}, ${response.status}`)
            }

            return response;

            // Since no content is expected, you might not need to return the response
            // But you can return the status for confirmation or further checks
        } catch (error) {
            throw error; // Allowing the caller to handle errors
        }
    }




    constructAuthenticationMethodCard(method, formattedDate, buttonClassSuffix, enabledOrDisabled) {
        const infoButtonId = `info-btn-${buttonClassSuffix}-${method.id}`;
        const deleteButtonId = `delete-btn-${buttonClassSuffix}-${method.id}`;
        const modalId = `modal-${buttonClassSuffix}-${method.id}`;
        // const cardId = `${method.id}`;

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
                <div class="card my-2" id=${modalId}>
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

            this.baseUIBinder.displayNotification('User lookup successful', 'alert-info', 5000);

        } catch (error) {
            this.baseUIBinder.displayNotification(`${error} `, 'alert-danger');
            console.log(error);
        } finally {
            this.uiBinder.spinner.hide();
            this.appUtils.setUserPrincipalNameQueryParam(this.uiBinder.userPrincipalName.val());
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

    // check if userprincipalname is in the url as a query parameter, if it is print hello world
    // ?userPrincipalName=vicre-test01@dtudk.onmicrosoft.com
    const urlParams = new URLSearchParams(window.location.search);
    const userPrincipalName = urlParams.get('userPrincipalName');
    if (userPrincipalName) {
        app.uiBinder.userPrincipalName.val(userPrincipalName);
        app.handleUserLookup(new Event('click'));
    }


});










