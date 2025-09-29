console.log('Frontpage JS loaded');


class App {
    constructor(uiBinder = UIBinder.getInstance(), baseUIBinder = BaseUIBinder.getInstance(), appUtils = AppUtils.getInstance(), baseAppUtils = BaseAppUtils.getInstance()) {

        if (!App.instance) {
            this.uiBinder = uiBinder;
            this.baseUIBinder = baseUIBinder;
            this.appUtils = appUtils;
            this.baseAppUtils = baseAppUtils;
            this.selectedLimiterTypes = new Set();
            this._setBindings();
            App.instance = this;
        }

        return App.instance;
    }


    _setBindings() {

        // // Set binding for user lookup form submission
        // this.uiBinder.generateTokenBtn.on('click', (event) => {
        //     event.preventDefault();
        //     this.handleCreateNewApiTokenBtn(event, this);
        // });

        if (this.uiBinder.generateTokenBtn.length) {
            const generateTokenBtn = `#${this.uiBinder.generateTokenBtn[0].id}`; // this is the button that will trigger the modal
            const modalId = 'tokenDisplayModal';
            const modalConfirmBtn = 'modalConfirmBtn'; // these are refering to elements generation innside the modal, not the main page
            this.baseAppUtils.setModal(generateTokenBtn, modalId, {
                title: 'Generate New Token',
                body: '<p>The token will only be displayed once, are you sure you want to generate a new token?</p>',
                footer: `
                    <button type="button" class="btn btn-danger" id="${modalConfirmBtn}">Generate New Token <span id="loadingSpinnerGenerateTokenBtn" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" style="display: none;"></span></button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">No, Cancel</button>
                `,
                eventListeners: [
                    {
                        selector: '#modalConfirmBtn',
                        event: 'click',
                        handler: (event) => {
                            // how do i access modalId in this scope?
                            this.handleCreateNewApiToken(event, modalId, this);
                        }
                    }
                ]
            });
        }

        if (this.uiBinder.filterLimiterTypeBtn.length) {
            const filterLimiterBtnSelector = `#${this.uiBinder.filterLimiterTypeBtn[0].id}`;
            const limiterModalId = 'limiterTypeFilterModal';
            const availableLimiterTypes = this.appUtils.getAvailableLimiterTypes();

            const modalBody = this.appUtils.generateLimiterTypeOptionsHtml(availableLimiterTypes);
            const modalFooter = `
                <button type="button" class="btn btn-primary" id="applyLimiterFilterBtn">Apply filter</button>
                <button type="button" class="btn btn-outline-secondary" id="clearLimiterFilterBtn">Clear filter</button>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            `;

            this.baseAppUtils.setModal(filterLimiterBtnSelector, limiterModalId, {
                title: 'Filter endpoints by limiter type',
                body: modalBody,
                footer: modalFooter,
                eventListeners: [
                    {
                        selector: '#applyLimiterFilterBtn',
                        event: 'click',
                        handler: (event) => {
                            this.handleApplyLimiterFilter(event, limiterModalId);
                        }
                    },
                    {
                        selector: '#clearLimiterFilterBtn',
                        event: 'click',
                        handler: (event) => {
                            this.handleClearLimiterFilter(event, limiterModalId);
                        }
                    }
                ]
            });

            const limiterModalElement = document.getElementById(limiterModalId);
            if (limiterModalElement) {
                limiterModalElement.addEventListener('show.bs.modal', () => {
                    this.populateLimiterModalSelections(limiterModalId);
                });
            }
        }

        this.updateLimiterFilterSummary();
        this.filterEndpointTable();
    }




    async handleCreateNewApiToken(event, modalId, app = App.getInstance()) {
        event.preventDefault();
        const button = $(this);
        const spinner = $('#loadingSpinnerGenerateTokenBtn');
        // Show the spinner and disable the button
        spinner.show();
        button.prop('disabled', true);

        // set a modal to display the token a
        let formData = new FormData();
        formData.append('action', 'create_custom_token');

        let response;
        let errorOccurred = false;
        try {
            response = await app.baseAppUtils.restAjax('POST', '/myview/ajax/', formData);
        } catch (error) {
            console.log('Error:', error);
            app.baseUIBinder.displayNotification(error, 'alert-danger')
            errorOccurred = true;
        } finally {
            if (!errorOccurred) {
                // if success
                app.baseUIBinder.displayNotification('Token generated successfully!', 'alert-success');

                const token = response.custom_token;
                
                const modalBody = `
                <p>Your new token is:</p>
                <pre id="token">${token}</pre>
                <button id="copyButton" type="button" class="btn btn-primary">Copy Token</button>
                <span id="copyMessage" style="display: none;">Copied!</span>
                `

                const eventListeners = [
                    {
                        selector: '#copyButton',
                        event: 'click',
                        handler: (event) => {
                            const token = document.getElementById('token').innerText;
                            navigator.clipboard.writeText(token);

                            let copyMessage = document.getElementById('copyMessage');
                            copyMessage.style.display = 'inline';
                            setTimeout(function () {
                                copyMessage.style.display = 'none';
                            }, 800);  // Message will disappear after 2 seconds
                        }
                    }
                ]

                app.baseAppUtils.updateModalContent(modalId, {modalBody: modalBody, eventListeners});
            }

            // Hide the spinner and enable the button
            spinner.hide();
            button.prop('disabled', false);
        }


    }

    handleApplyLimiterFilter(event, modalId) {
        event.preventDefault();
        const selectedCheckboxes = Array.from(document.querySelectorAll(`#${modalId} input[type="checkbox"]:checked`));
        const selectedValues = selectedCheckboxes.map((checkbox) => checkbox.value);

        this.selectedLimiterTypes = new Set(selectedValues);
        this.filterEndpointTable();
        this.updateLimiterFilterSummary();

        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    }

    handleClearLimiterFilter(event, modalId) {
        event.preventDefault();
        this.selectedLimiterTypes.clear();
        this.filterEndpointTable();
        this.updateLimiterFilterSummary();
        this.populateLimiterModalSelections(modalId);
    }

    filterEndpointTable() {
        const rows = document.querySelectorAll('[data-endpoint-row]');
        const hasActiveFilters = this.selectedLimiterTypes && this.selectedLimiterTypes.size > 0;

        rows.forEach((row) => {
            const limiterType = (row.getAttribute('data-limiter-type') || 'None').trim() || 'None';
            if (!hasActiveFilters || this.selectedLimiterTypes.has(limiterType)) {
                row.classList.remove('d-none');
            } else {
                row.classList.add('d-none');
            }
        });
    }

    populateLimiterModalSelections(modalId) {
        const modalElement = document.getElementById(modalId);
        if (!modalElement) {
            return;
        }

        const checkboxes = modalElement.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach((checkbox) => {
            if (!this.selectedLimiterTypes || this.selectedLimiterTypes.size === 0) {
                checkbox.checked = false;
            } else {
                checkbox.checked = this.selectedLimiterTypes.has(checkbox.value);
            }
        });
    }

    updateLimiterFilterSummary() {
        if (!this.uiBinder.limiterFilterSummary || this.uiBinder.limiterFilterSummary.length === 0) {
            return;
        }

        if (!this.selectedLimiterTypes || this.selectedLimiterTypes.size === 0) {
            this.uiBinder.limiterFilterSummary.text('');
            this.uiBinder.limiterFilterSummary.addClass('d-none');
            return;
        }

        const summaryText = Array.from(this.selectedLimiterTypes).join(', ');
        this.uiBinder.limiterFilterSummary.text(summaryText);
        this.uiBinder.limiterFilterSummary.removeClass('d-none');
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


    getAvailableLimiterTypes() {
        if (this.availableLimiterTypes) {
            return this.availableLimiterTypes;
        }

        const scriptElement = document.getElementById('available-limiter-types-data');
        if (!scriptElement) {
            this.availableLimiterTypes = [];
            return this.availableLimiterTypes;
        }

        try {
            const parsedData = JSON.parse(scriptElement.textContent);
            this.availableLimiterTypes = Array.isArray(parsedData) ? parsedData : [];
        } catch (error) {
            console.error('Failed to parse available limiter types:', error);
            this.availableLimiterTypes = [];
        }

        return this.availableLimiterTypes;
    }

    escapeHtml(value) {
        if (typeof value !== 'string') {
            return '';
        }

        return value
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    generateLimiterTypeOptionsHtml(limiterTypes = []) {
        if (!Array.isArray(limiterTypes) || limiterTypes.length === 0) {
            return '<p class="mb-0">No limiter types available.</p>';
        }

        const optionsHtml = limiterTypes.map((type, index) => {
            const safeValue = typeof type === 'string' ? type.trim() : '';
            const escapedLabel = this.escapeHtml(safeValue || 'None');
            const checkboxId = `limiterTypeOption-${index}`;
            return `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${escapedLabel}" id="${checkboxId}">
                    <label class="form-check-label" for="${checkboxId}">${escapedLabel}</label>
                </div>
            `;
        }).join('');

        return `<fieldset><legend class="visually-hidden">Limiter type filters</legend>${optionsHtml}</fieldset>`;
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
            this.generateTokenBtn = $('#generateTokenBtn');
            this.filterLimiterTypeBtn = $('#filterLimiterTypeBtn');
            this.limiterFilterSummary = $('#limiterFilterSummary');
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
