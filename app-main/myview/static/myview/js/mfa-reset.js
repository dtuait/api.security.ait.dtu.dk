console.log('MFA Reset JS loaded');

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
        this.uiBinder.mfaUserLookupSubmitBtn.on('click', this.handleUserLookUpbinder.bind(this));
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

    async validateUserPrincipalName(userPrincipalName) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!userPrincipalName) {
            throw new Error('userPrincipalName field cannot be empty.');
        }
        if (!emailRegex.test(userPrincipalName)) {
            throw new Error('Invalid userPrincipalName format.');
        }
        return true;
    }

    async getUserAuthenticationMethods(app) {
        const userPrincipalName = app.uiBinder.userPrincipalName.val();
        const url = `/graph/v1.0/list/${encodeURIComponent(userPrincipalName)}/authentication-methods`;
        const response = await app.baseAppUtils.restAjax('GET', url);
        return response;
    }

    async fetchAndDisplayUserAuthenticationMethods(app) {
        const userAuthenticationMethods = await this.getUserAuthenticationMethods(app);
    
        // Filter out relevant MFA methods
        const mfaMethods = userAuthenticationMethods.value.filter(method => 
            method["@odata.type"] === '#microsoft.graph.phoneAuthenticationMethod' || 
            method["@odata.type"] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod'
        );
    
        // Clear the card container
        app.uiBinder.cardsContainer.empty();
    
        // Create a single card with details or show a message if no MFA methods are found
        if (mfaMethods.length > 0) {
            const methodDetails = mfaMethods.map(method => {
                return `<p>${method["@odata.type"]}: ${method.id}</p>`;
            }).join('');
    
            const cardHtml = `
                <div class="card my-2">
                    <div class="card-body">
                        <h5 class="card-title">Reset MFA</h5>
                        ${methodDetails}
                        <button class="btn btn-danger" id="mfa-reset-btn">Reset MFA</button>
                    </div>
                </div>
            `;
            app.uiBinder.cardsContainer.append(cardHtml);
    
            // Enable and bind the reset button
            $('#mfa-reset-btn').on('click', async function (event) {
                event.preventDefault();
                try {
                    await app.appUtils.resetMFA(app, mfaMethods);
                    app.baseUIBinder.displayNotification('MFA reset successfully. Reloads in 2 seconds.', 'alert-success', 2000);
                } catch (error) {
                    app.baseUIBinder.displayNotification(`${error} `, 'alert-danger');
                    console.log(error);
                }
            });
        } else {
            const noMfaMessage = `
                <div class="alert alert-warning" role="alert">
                    No MFA methods found for this user.
                </div>
            `;
            app.uiBinder.cardsContainer.append(noMfaMessage);
        }
    }
    
    async resetMFA(app, mfaMethods) {
        const userPrincipalName = app.uiBinder.userPrincipalName.val();
        try {
            for (const method of mfaMethods) {
                if (method["@odata.type"] === '#microsoft.graph.phoneAuthenticationMethod') {
                    await this.deletePhoneAuthenticationMethod(app, userPrincipalName, method.id);
                } else if (method["@odata.type"] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
                    await this.deleteMicrosoftAuthenticationMethod(app, userPrincipalName, method.id);
                }
            }
            app.baseUIBinder.displayNotification('All MFA methods have been successfully reset.', 'alert-success');
            setTimeout(() => {
                location.reload();
            }, 2000);
        } catch (error) {
            throw new Error('Failed to reset MFA methods: ' + error.message);
        }
    }

    async deleteMicrosoftAuthenticationMethod(app, userEmail, authID) {
        const url = `/graph/v1.0/users/${encodeURIComponent(userEmail)}/microsoft-authentication-methods/${authID}`;
        const headers = {
            'accept': 'application/json'
        };
        return await app.baseAppUtils.restAjax('DELETE', url, { headers: headers });
    }

    async deletePhoneAuthenticationMethod(app, userEmail, authID) {
        const url = `/graph/v1.0/users/${encodeURIComponent(userEmail)}/phone-authentication-methods/${authID}`;
        const headers = {
            'accept': 'application/json'
        };
        return await app.baseAppUtils.restAjax('DELETE', url, { headers: headers });
    }

    async handleUserLookup(event, app) {
        event.preventDefault();
        app.uiBinder.spinner.show();
        app.uiBinder.mfaUserLookupSubmitBtn.prop('disabled', true);
        try {
            await this.validateUserPrincipalName(app.uiBinder.userPrincipalName.val());
            await this.fetchAndDisplayUserAuthenticationMethods(app);
            app.baseUIBinder.displayNotification('User lookup successful', 'alert-info', 5000);
        } catch (error) {
            app.baseUIBinder.displayNotification(`${error} `, 'alert-danger');
            console.log(error);
        } finally {
            app.uiBinder.spinner.hide();
            app.appUtils.setUserPrincipalNameQueryParam(app.uiBinder.userPrincipalName.val());
            app.uiBinder.mfaUserLookupSubmitBtn.prop('disabled', false);
        }
    }

    setUserPrincipalNameQueryParam(userPrincipalName) {
        const currentUrl = new URL(window.location);
        const searchParams = currentUrl.searchParams;
        searchParams.set('userPrincipalName', userPrincipalName);
        const newUrl = `${currentUrl.origin}${currentUrl.pathname}?${searchParams.toString()}`;
        window.history.pushState({ path: newUrl }, '', newUrl);
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
    const urlParams = new URLSearchParams(window.location.search);
    const userPrincipalName = urlParams.get('userPrincipalName');
    if (userPrincipalName) {
        app.uiBinder.userPrincipalName.val(userPrincipalName);
        app.handleUserLookUpbinder(new Event('click'));
    }
});
