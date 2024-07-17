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

    handleUserLookup(event) {
        event.preventDefault();

        // this.baseUIBinder.displayNotification("Hello World", "alert-info");
        this.uiBinder.spinner.show();
        this.uiBinder.mfaUserLookupSubmitBtn.prop('disabled', true);

        try {

            this.appUtils.validateUserPrincipalName(this.uiBinder.userPrincipalName.val());
            this.baseUIBinder.displayNotification('User lookup successful', 'alert-info');

        } catch (error) {
            this.baseUIBinder.displayNotification(`Error: ${error}` , 'alert-danger');
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
    // Initialize the UI manager for mfa-reset page
    // baseUIManager is defiened in base.js
    // const baseUIBinder = BaseUIBinder.getInstance();    // Get the instance of BaseUIManager
    // const baseAppUtils = BaseAppUtils.getInstance();    // Get the instance of BaseApp
    // const appUtils = AppUtils.getInstance();            // Get the instance of App
    // const uiBinder = UIBinder.getInstance();           // Create an instance of UIManager


    const app = App.getInstance();


});










