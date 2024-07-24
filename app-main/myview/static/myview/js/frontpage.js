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
        
        // Set binding for user lookup form submission
        this.uiBinder.deleteADGroupCacheBtn.on('click', (event) => {
                // pass the event and the app instance to the function
                this.deleteADGroupCache(event, this)
            });
    }





    async deleteADGroupCache(event, app) {

        app.uiBinder.deleteADGroupCacheBtn.prop('disabled', true);
        app.uiBinder.loadingSpinnerDeleteADGroupCacheBtn.show();

        let formData = new FormData();
        formData.append('action', 'clear_my_ad_group_cached_data');

        let response;

        try {
            response = await app.baseAppUtils.restAjax('POST', '/myview/ajax/', {data:formData});
        } catch (error) {
            console.log('Error:', error);
            app.baseUIBinder.displayNotification(error, 'alert-danger')
        } finally {
            if (response?.status === 200) {
                app.baseUIBinder.displayNotification('this is a test', 'alert-info')
                // Wait for 2 seconds
                setTimeout(function () {
                    // reload the page
                    location.reload();
                }, 2000);

            }
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







class UIBinder {
    constructor() {
        if (!UIBinder.instance) {
            this.deleteADGroupCacheBtn = $('#deleteADGroupCacheBtn');            
            this.loadingSpinnerDeleteADGroupCacheBtn = $('#loadingSpinnerDeleteADGroupCacheBtn');
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
