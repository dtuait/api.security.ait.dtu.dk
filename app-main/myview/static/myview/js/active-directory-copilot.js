console.log('Active Directory Copilot JS loaded');

class CopilotApp {
    constructor(uiBinder = CopilotUIBinder.getInstance(), baseUIBinder = BaseUIBinder.getInstance(), appUtils = CopilotAppUtils.getInstance(), baseAppUtils = BaseAppUtils.getInstance()) {
        if (!CopilotApp.instance) {
            this.uiBinder = uiBinder;
            this.baseUIBinder = baseUIBinder;
            this.appUtils = appUtils;
            this.baseAppUtils = baseAppUtils;
            this._setBindings();
            CopilotApp.instance = this;
        }

        return CopilotApp.instance;
    }

    _setBindings() {
        this.uiBinder.copilotSubmitBtn.on('click', this.handleCopilotRequest.bind(this));

        this.uiBinder.copilotTextareaField.on('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                this.handleCopilotRequest(event);
            }
        }).on('input', function() {
            var text = $(this).val();
            var cols = $(this).attr('cols');
            var lineCount = (text.match(/\n/g) || []).length + 1;
            var wrappedLineCount = Math.ceil(text.length / cols);
            var totalLineCount = Math.max(lineCount, wrappedLineCount);
            $(this).attr('rows', totalLineCount);
        });

        this.uiBinder.downloadJsonBtn.on('click', this.appUtils.downloadJsonFile.bind(this.appUtils));
    }

    async handleCopilotRequest(event) {
        event.preventDefault();
        console.log("Handling copilot request");

        var textareaValue = this.uiBinder.copilotTextareaField.val();
        console.log(textareaValue);

        let formData = new FormData();
        formData.append('action', 'copilot-active-directory-query');
        formData.append('content', JSON.stringify({ user: textareaValue }));

        this.uiBinder.loadingSpinnerCopilot.show();
        this.uiBinder.copilotSubmitBtn.prop('disabled', true);

        let response;

        try {
            response = await this.baseAppUtils.restAjax('POST', '/myview/ajax/', { data: formData });

            if (response.active_directory_query_result) {
                console.log(response);

                // Display the result
                this.uiBinder.copilotResultContainer.show();
                this.uiBinder.copilotResult.text(JSON.stringify(response, null, 2));

                // Store the result for download
                this.appUtils.queryResult = response;

            } else if (response.error) {
                this.baseUIBinder.displayNotification(response.error, 'alert-warning');
            } else {
                this.baseUIBinder.displayNotification('An unknown error occurred.', 'alert-warning');
            }
        } catch (error) {
            console.log('Error:', error);
            this.baseUIBinder.displayNotification('An error occurred while processing your request.', 'alert-danger');
        } finally {
            this.uiBinder.loadingSpinnerCopilot.hide();
            this.uiBinder.copilotSubmitBtn.prop('disabled', false);
        }
    }

    static getInstance(uiBinder = CopilotUIBinder.getInstance(), baseUIBinder = BaseUIBinder.getInstance(), appUtils = CopilotAppUtils.getInstance(), baseAppUtils = BaseAppUtils.getInstance()) {
        if (!CopilotApp.instance) {
            CopilotApp.instance = new CopilotApp(uiBinder, baseUIBinder, appUtils, baseAppUtils);
        }
        return CopilotApp.instance;
    }
}

class CopilotAppUtils {
    constructor() {
        if (!CopilotAppUtils.instance) {
            this.queryResult = null; // Store the result for downloading
            CopilotAppUtils.instance = this;
        }
        return CopilotAppUtils.instance;
    }

    downloadJsonFile() {
        if (this.queryResult) {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.queryResult, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "active_directory_query_result.json");
            document.body.appendChild(downloadAnchorNode); // Required for Firefox
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        }
    }

    static getInstance() {
        if (!CopilotAppUtils.instance) {
            CopilotAppUtils.instance = new CopilotAppUtils();
        }
        return CopilotAppUtils.instance;
    }
}

class CopilotUIBinder {
    constructor() {
        if (!CopilotUIBinder.instance) {
            this.copilotForm = $('#copilot-form');
            this.copilotSubmitBtn = $('#copilot-submit-btn');
            this.copilotTextareaField = $('#copilot-submit-textarea-field');
            this.loadingSpinnerCopilot = $('#loadingSpinnerCopilot');
            this.copilotResultContainer = $('#copilot-result-container');
            this.copilotResult = $('#copilot-result');
            this.downloadJsonBtn = $('#download-json-btn');
            CopilotUIBinder.instance = this;
        }

        return CopilotUIBinder.instance;
    }

    static getInstance() {
        if (!CopilotUIBinder.instance) {
            CopilotUIBinder.instance = new CopilotUIBinder();
        }
        return CopilotUIBinder.instance;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const app = CopilotApp.getInstance();
});