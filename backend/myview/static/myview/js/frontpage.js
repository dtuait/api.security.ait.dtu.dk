// frontpage.js

console.log('Frontpage JS loaded');

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
        const generateTokenBtnSelector = `#${this.uiBinder.generateTokenBtn.id}`; // Selector string for the trigger
        const modalId = 'tokenDisplayModal';
        const modalConfirmBtn = 'modalConfirmBtn'; // ID for the confirm button inside the modal

        this.baseAppUtils.setModal(generateTokenBtnSelector, modalId, {
            title: 'Generate New Token',
            body: '<p>The token will only be displayed once, are you sure you want to generate a new token?</p>',
            footer: `
                <button type="button" class="btn btn-danger" id="${modalConfirmBtn}">Generate New Token <span id="loadingSpinnerGenerateTokenBtn" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" style="display: none;"></span></button>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">No, Cancel</button>
            `,
            eventListeners: [
                {
                    selector: `#${modalConfirmBtn}`,
                    event: 'click',
                    handler: (event) => {
                        this.handleCreateNewApiToken(event, modalId, this);
                    }
                }
            ]
        });
    }

    async handleCreateNewApiToken(event, modalId, app = App.getInstance()) {
        event.preventDefault();
        const button = event.currentTarget;
        const spinner = document.getElementById('loadingSpinnerGenerateTokenBtn');
        // Show the spinner and disable the button
        spinner.style.display = 'inline-block';
        button.disabled = true;

        // Prepare form data
        let formData = new FormData();
        formData.append('action', 'create_custom_token');

        let response;
        let errorOccurred = false;
        try {
            response = await app.baseAppUtils.restAjax('POST', '/myview/ajax/', formData);
        } catch (error) {
            console.log('Error:', error);
            app.baseUIBinder.displayNotification(error.message, 'alert-danger');
            errorOccurred = true;
        } finally {
            if (!errorOccurred) {
                // If success
                app.baseUIBinder.displayNotification('Token generated successfully!', 'alert-success');

                const token = response.custom_token;

                const modalBody = `
                    <p>Your new token is:</p>
                    <pre id="token">${token}</pre>
                    <button id="copyButton" type="button" class="btn btn-primary">Copy Token</button>
                    <span id="copyMessage" style="display: none;">Copied!</span>
                `;

                const eventListeners = [
                    {
                        selector: '#copyButton',
                        event: 'click',
                        handler: (event) => {
                            const tokenText = document.getElementById('token').innerText;
                            navigator.clipboard.writeText(tokenText);

                            let copyMessage = document.getElementById('copyMessage');
                            copyMessage.style.display = 'inline';
                            setTimeout(function () {
                                copyMessage.style.display = 'none';
                            }, 800); // Message will disappear after 800 milliseconds
                        }
                    }
                ];

                app.baseAppUtils.updateModalContent(modalId, { modalBody: modalBody, eventListeners });
            }

            // Hide the spinner and enable the button
            spinner.style.display = 'none';
            button.disabled = false;
        }
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
        return "Hello World";
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
            this.generateTokenBtn = document.getElementById('generateTokenBtn');
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
