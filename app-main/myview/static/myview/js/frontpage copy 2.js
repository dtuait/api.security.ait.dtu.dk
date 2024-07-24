console.log('Frontpage JS loaded');





// function showTokenSubModal(token) {
//     const subModalId = 'tokenDisplayModal';
//     const modalHtml = `
//     <div class="modal fade" id="${subModalId}" tabindex="-1" aria-labelledby="${subModalId}Label" aria-hidden="true">
//     <div class="modal-dialog">
//         <div class="modal-content">
//             <div class="modal-header">
//                 <h5 class="modal-title" id="${subModalId}Label">Your New Token</h5>
//                 <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
//             </div>
//             <div class="modal-body">
//                 <p>Your new token is:</p>
//                 <pre id="token">${token}</pre>
//                 <button id="copyButton" type="button" class="btn btn-primary">Copy Token</button>
//                 <span id="copyMessage" style="display: none;">Copied!</span>
//             </div>
//             <div class="modal-footer">
//                 <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
//             </div>
//         </div>
//     </div>
// </div>

// <script>
// document.getElementById('copyButton').addEventListener('click', function() {
//     var token = document.getElementById('token').innerText;
//     navigator.clipboard.writeText(token);

//     var copyMessage = document.getElementById('copyMessage');
//     copyMessage.style.display = 'inline';
//     setTimeout(function() {
//         copyMessage.style.display = 'none';
//     }, 800);  // Message will disappear after 2 seconds
// });
// </script>
//     `;
//     $('body').append(modalHtml);

//     const subModalInstance = new bootstrap.Modal(document.getElementById(subModalId));
//     subModalInstance.show();
// }


// setModal(`#generateTokenBtn`, `generateTokenBtnModal`, {
//     title: 'Generate New Token',
//     body: 'The token will only be displayed once, are you sure you want to generate a new token?',
//     footer: `
//         <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
//         <button type="button" class="btn btn-primary" id="confirmSyncAdUsersBtn">Generate New Token <span id="loadingSpinnerGenerateTokenBtn" class="spinner-border spinner-border-sm" role="status" aria-hidden="true" style="display: none;"></span></button>
//     `,
//     eventListeners: [
//         {
//             selector: '#confirmSyncAdUsersBtn',
//             event: 'click',
//             handler: async function () {
//             const button = $(this);
//             const spinner = $('#loadingSpinnerGenerateTokenBtn');
//             // Show the spinner and disable the button
//             spinner.show();
//             button.prop('disabled', true);

            
//             let formData = new FormData();     
//             formData.append('action', 'create_custom_token');       

            
//             let response;
            
//             try {
//                 response = await restAjax('POST', '/myview/ajax/', formData);
//                 const modalElement = document.getElementById('generateTokenBtnModal');
//                 const modalInstance = bootstrap.Modal.getInstance(modalElement);
//                 modalInstance.hide();

//             } catch (error) {
//                 console.log('Error:', error);
//             } finally {
//                 if (response.status === 200) {
//                     displayNotification('Token generated successfully!', 'success');
//                     showTokenSubModal(response.data.custom_token);
//                     // Hide the spinner and enable the button
//                     spinner.hide();
//                     button.prop('disabled', false);


//                 } else if (response.error) {
//                     displayNotification(response.error, 'warning');
//                 } else {
//                     displayNotification('An unknown error occurred.', 'warning');
//                 }
//             }

//             }
            
//         },
//     ]
// })





async function deleteADGroupCache() {
    const button = $(this);
    const spinner = $('#loadingSpinnerDeleteADGroupCacheBtn');
    // Show the spinner and disable the button
    spinner.show();
    button.prop('disabled', true);

    let formData = new FormData();     
    formData.append('action', 'clear_my_ad_group_cached_data');
    let response;
    try {
        response = await restAjax('POST', '/myview/ajax/', formData);
    } catch (error) {
        console.log('Error:', error);
    } finally {
        if (response.status === 200) {
            displayNotification('Cache deleted successfully!, reloading page in 2 seconds', 'success');

            // Wait for 2 seconds
            setTimeout(function() {
                // reload the page
                location.reload();
            }, 2000);






        } else if (response.error) {
            displayNotification(response.error, 'warning');
        } else {
            displayNotification('An unknown error occurred.', 'warning');
        }
    }
}

// using jquery add a eventlisten (click) on <button id="deleteADGroupCacheBtn" class="btn btn-primary"> that runs deleteADGroupCache()
$('#deleteADGroupCacheBtn').on('click', deleteADGroupCache);



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

            this.deleteADGroupCacheBtn = $('#deleteADGroupCacheBtn');
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
















document.addEventListener('DOMContentLoaded', function () {
    const app = App.getInstance();
});
