// mfa-reset.js

console.log('MFA Reset JS loaded');

import { BaseUIBinder, BaseAppUtils } from './base-classes.js';

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
        this.uiBinder.mfaUserLookupSubmitBtn.addEventListener('click', this.handleUserLookUpbinder.bind(this));
    }

    handleUserLookUpbinder(event) {
        event.preventDefault();
        this.appUtils.handleUserLookup(event, this);
    }

    static getInstance(uiBinder = UIBinder.getInstance(), baseUIBinder = BaseUIBinder.getInstance(), appUtils = AppUtils.getInstance(), baseAppUtils = BaseAppUtils.getInstance()) {
        if (!App.instance) {
            App.instance = new App(uiBinder, baseUIBinder, appUtils, baseAppUtils);
        }
        return App.instance;
    }
}

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
        const userPrincipalName = app.uiBinder.userPrincipalName.value;  // Get the userPrincipalName
        const url = `/graph/v1.0/list/${encodeURIComponent(userPrincipalName)}/authentication-methods`;

        const response = await app.baseAppUtils.restAjax('GET', url);

        return response;
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
            buttonClassSuffix = 'mfa';
            enabledOrDisabled = 'enabled';
        } else if (method['@odata.type'] === '#microsoft.graph.phoneAuthenticationMethod') {
            buttonClassSuffix = 'phone';
            enabledOrDisabled = 'enabled';
        } else if (method['@odata.type'] === '#microsoft.graph.softwareOathAuthenticationMethod') {
            buttonClassSuffix = 'software-oath';
            enabledOrDisabled = 'enabled';
        } else {
            buttonClassSuffix = 'undetermined';
            enabledOrDisabled = 'disabled';
        }
        modalOptions = this.assignModalOptions(protocol, server, port, buttonClassSuffix);
        return { buttonClassSuffix, enabledOrDisabled, modalOptions };
    }

    assignModalOptions(protocol, server, port, buttonClassSuffix) {
        let modalOptions = { title: '', body: '' };
        if (buttonClassSuffix === 'mfa') {
            modalOptions.title = 'Microsoft Authenticator Method';
            modalOptions.body = 'This authentication method is Microsoft Authenticator.';
        } else if (buttonClassSuffix === 'phone') {
            modalOptions.title = 'Phone Method';
            modalOptions.body = 'This authentication method is Phone.';
        } else if (buttonClassSuffix === 'software-oath') {
            modalOptions.title = 'Software Oath Method';
            modalOptions.body = 'This authentication method is Software Oath.';
        } else {
            modalOptions.title = `This is an undetermined method`;
            modalOptions.body = `This authentication method is disabled because it is not an MFA method. If you want to DELETE it, you can do it via the API:<br><a href="${protocol}//${server}:${port}/myview/swagger/">${protocol}//${server}:${port}/myview/swagger/</a>`;
        }
        return modalOptions;
    }

    async fetchAndDisplayUserAuthenticationMethods(app) {
        const userAuthenticationMethods = await this.getUserAuthenticationMethods(app);
        // Clear the card container
        app.uiBinder.cardsContainer.innerHTML = '';
        userAuthenticationMethods.value.forEach(authenticationMethod => {
            this.displayAuthenticationMethod(app, authenticationMethod);
        });
    }

    async deleteSoftwareAuthenticationMethod(app, userEmail, authID) {
        const url = `/graph/v1.0/users/${encodeURIComponent(userEmail)}/software-authentication-methods/${authID}`;
        const headers = {
            'accept': 'application/json'
        };

        const response = await app.baseAppUtils.restAjax('DELETE', url, null, headers);
        return response;
    }

    displayAuthenticationMethod(app, authenticationMethod) {
        try {
            const userPrincipalName = app.uiBinder.userPrincipalName.value;  // Get the userPrincipalName
            const { formattedDate, buttonClassSuffix, enabledOrDisabled, modalOptions } = this.prepareMethodDetails(authenticationMethod);

            const card = this.constructAuthenticationMethodCard(authenticationMethod, formattedDate, buttonClassSuffix, enabledOrDisabled);

            // Append the card HTML to the cards container
            app.uiBinder.cardsContainer.insertAdjacentHTML('beforeend', card.card);

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
                        handler: async () => {
                            try {
                                console.log("deleteConfirmButtonId clicked");
                                if (buttonClassSuffix === 'mfa') {
                                    await app.appUtils.deleteMicrosoftAuthenticationMethod(app, userPrincipalName, authenticationMethod.id);
                                } else if (buttonClassSuffix === 'phone') {
                                    await app.appUtils.deletePhoneAuthenticationMethod(app, userPrincipalName, authenticationMethod.id);
                                } else if (buttonClassSuffix === 'software-oath') {
                                    await app.appUtils.deleteSoftwareAuthenticationMethod(app, userPrincipalName, authenticationMethod.id);
                                } else {
                                    throw new Error(`This authentication method is disabled because it is not an MFA method. If you want to DELETE it, you can do it via the API.`);
                                }
                                app.baseUIBinder.displayNotification(`The authentication method was successfully deleted. Refreshing the page in 2 seconds`, 'alert-success');
                                app.appUtils.setUserPrincipalNameQueryParam(userPrincipalName);
                                setTimeout(() => {
                                    location.reload();
                                }, 2000);
                            } catch (error) {
                                app.baseUIBinder.displayNotification(`${error} `, 'alert-danger');
                                console.log(error);
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

            // Set the modals using BaseAppUtils
            app.baseAppUtils.setModal(`#${card.deleteButtonId}`, `delete-${card.deleteButtonId}`, deleteModalOptions);
            app.baseAppUtils.setModal(`#${card.infoButtonId}`, `info-${card.modalId}`, modalOptions);

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

    async deleteMicrosoftAuthenticationMethod(app, userEmail, authID) {
        const url = `/graph/v1.0/users/${encodeURIComponent(userEmail)}/microsoft-authentication-methods/${authID}`;
        const headers = {
            'accept': 'application/json'
        };

        const response = await app.baseAppUtils.restAjax('DELETE', url, null, headers);
        return response;
    }

    async handleUserLookup(event, app) {
        event.preventDefault();

        app.uiBinder.spinner.style.display = 'inline-block';
        app.uiBinder.mfaUserLookupSubmitBtn.disabled = true;

        try {
            await app.appUtils.validateUserPrincipalName(app.uiBinder.userPrincipalName.value);
            await app.appUtils.fetchAndDisplayUserAuthenticationMethods(app);

            app.baseUIBinder.displayNotification('User lookup successful', 'alert-info', 5000);

        } catch (error) {
            app.baseUIBinder.displayNotification(`${error} `, 'alert-danger');
            console.log(error);
        } finally {
            app.uiBinder.spinner.style.display = 'none';
            app.appUtils.setUserPrincipalNameQueryParam(app.uiBinder.userPrincipalName.value);
            app.uiBinder.mfaUserLookupSubmitBtn.disabled = false;
        }
    }

    async deletePhoneAuthenticationMethod(app, userEmail, authID) {
        const url = `/graph/v1.0/users/${encodeURIComponent(userEmail)}/phone-authentication-methods/${authID}`;
        const headers = {
            'accept': 'application/json'
        };

        const response = await app.baseAppUtils.restAjax('DELETE', url, null, headers);
        return response;
    }

    constructAuthenticationMethodCard(method, formattedDate, buttonClassSuffix, enabledOrDisabled) {
        const infoButtonId = `info-btn-${buttonClassSuffix}-${method.id}`;
        const deleteButtonId = `delete-btn-${buttonClassSuffix}-${method.id}`;
        const modalId = `modal-${buttonClassSuffix}-${method.id}`;

        let cardHtml = `
            <div class="card my-2" id="${modalId}">
                <div class="card-body">
                    <h5 class="card-title">${method['@odata.type']}</h5>
        `;

        Object.entries(method).forEach(([key, value]) => {
            if (key !== '@odata.type') {
                if (key === 'createdDateTime') {
                    cardHtml += `<p class="card-text">${key}: ${formattedDate || 'N/A'}</p>`;
                } else {
                    cardHtml += `<p class="card-text">${key}: ${value}</p>`;
                }
            }
        });

        cardHtml += `
                    <button class="btn btn-danger ${enabledOrDisabled}" id="${deleteButtonId}">Remove</button>
                    <button class="btn btn-info" id="${infoButtonId}">Info</button>
                </div>
            </div>
        `;

        return {
            infoButtonId,
            deleteButtonId,
            modalId,
            card: cardHtml
        };
    }

    static getInstance() {
        if (!AppUtils.instance) {
            AppUtils.instance = new AppUtils();
        }
        return AppUtils.instance;
    }
}

class UIBinder {
    constructor() {
        if (!UIBinder.instance) {
            this.mfaUserLookupSubmitBtn = document.getElementById('mfa-user-lookup-submit-btn');
            this.spinner = document.getElementById('loadingSpinner');
            this.userPrincipalName = document.getElementById('id-userprincipalname');
            this.cardsContainer = document.getElementById('cards-container');
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
    BaseAppUtils.initializeTooltips();

    // Check if userPrincipalName is in the URL as a query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const userPrincipalName = urlParams.get('userPrincipalName');
    if (userPrincipalName) {
        app.uiBinder.userPrincipalName.value = userPrincipalName;
        app.handleUserLookUpbinder(new Event('click'));
    }
});
