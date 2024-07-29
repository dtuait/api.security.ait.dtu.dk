console.log('Frontpage JS loaded');





























































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

        // // Set binding for user lookup form submission
        // this.uiBinder.generateTokenBtn.on('click', (event) => {
        //     event.preventDefault();
        //     this.handleCreateNewApiTokenBtn(event, this);
        // });

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
                        this.handleCreateNewApiToken(event, this);
                    }

                    // handler: async function () {
                    //     const button = $(this);
                    //     const spinner = $('#loadingSpinnerGenerateTokenBtn');
                    //     // Show the spinner and disable the button
                    //     spinner.show();
                    //     button.prop('disabled', true);
                    //     alert('Save button clicked');

                    //     let formData = new FormData(); 
                    //     formData.append('action', 'create_custom_token');

                    //     let response;
                    // }
                }
            ]
        });

    }




    async handleCreateNewApiToken(event, app = App.getInstance()) {
        event.preventDefault();
        const button = $(this);
        const spinner = $('#loadingSpinnerGenerateTokenBtn');
        // Show the spinner and disable the button
        spinner.show();
        button.prop('disabled', true);

        // set a modal to display the token
        let formData = new FormData();
        formData.append('action', 'create_custom_token');

        let response;
        let errorOccurred = false;
        try {
            response = await app.baseAppUtils.restAjax('POST', '/myview/ajax/', { data: formData });
        } catch (error) {
            console.log('Error:', error);
            app.baseUIBinder.displayNotification(error, 'alert-danger')
            errorOccurred = true;
        } finally {
            if (!errorOccurred) {
                // if success
                app.baseUIBinder.displayNotification('Token generated successfully!', 'alert-success');
                app.appUtils.showTokenSubModal(response.custom_token);
            }
            
            // Hide the spinner and enable the button
            spinner.hide();
            button.prop('disabled', false);
        }


        // const button = $(this);
        // const spinner = $('#loadingSpinnerDeleteADGroupCacheBtn');
        // // Show the spinner and disable the button
        // spinner.show();
        // button.prop('disabled', true);

        // let formData = new FormData();
        // formData.append('action', 'clear_my_ad_group_cached_data');
        // let response;
        // try {
        //     response = await restAjax('POST', '/myview/ajax/', formData);
        // } catch (error) {
        //     console.log('Error:', error);
        // } finally {
        //     if (response.status === 200) {
        //         displayNotification('Cache deleted successfully!, reloading page in 2 seconds', 'success');

        //         // Wait for 2 seconds
        //         setTimeout(function () {
        //             // reload the page
        //             location.reload();
        //         }, 2000);






        //     } else if (response.error) {
        //         displayNotification(response.error, 'warning');
        //     } else {
        //         displayNotification('An unknown error occurred.', 'warning');
        //     }
        // }
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


    showTokenSubModal(token) {
        const subModalId = 'tokenDisplayModal';
        const modalHtml = `
    <div class="modal fade" id="${subModalId}" tabindex="-1" aria-labelledby="${subModalId}Label" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="${subModalId}Label">Your New Token</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p>Your new token is:</p>
                <pre id="token">${token}</pre>
                <button id="copyButton" type="button" class="btn btn-primary">Copy Token</button>
                <span id="copyMessage" style="display: none;">Copied!</span>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('copyButton').addEventListener('click', function() {
    var token = document.getElementById('token').innerText;
    navigator.clipboard.writeText(token);

    var copyMessage = document.getElementById('copyMessage');
    copyMessage.style.display = 'inline';
    setTimeout(function() {
        copyMessage.style.display = 'none';
    }, 800);  // Message will disappear after 2 seconds
});
</script>
    `;
        $('body').append(modalHtml);

        const subModalInstance = new bootstrap.Modal(document.getElementById(subModalId));
        subModalInstance.show();
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
