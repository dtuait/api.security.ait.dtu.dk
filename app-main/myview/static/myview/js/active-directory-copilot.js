
async function handleCopilotRequest(event) {
    event.preventDefault();
    console.log("Handling copilot request");

    var textareaValue = $('#copilot-submit-textarea-field').val();
    console.log(textareaValue);

    let formData = new FormData();     
    formData.append('action', 'copilot-chatgpt-basic');
    formData.append('content', JSON.stringify({user: textareaValue}))

    let response;
    
    try {
        response = await restAjax('POST', '/myview/ajax/', formData);
    } catch (error) {
        console.log('Error:', error);
    } finally {
        if (response.status === 200) {
            console.log(response.data);
        } else if (response.error) {
            displayNotification(response.error, 'warning');
        } else {
            displayNotification('An unknown error occurred.', 'warning');
        }
    } 


}

$('#copilot-submit-btn').on('click', handleCopilotRequest);


$('#copilot-submit-textarea-field').on('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleCopilotRequest(event)
        // console.log('User pressed Enter');
    }
}).on('input', function() {
    var text = $(this).val();
    var cols = $(this).attr('cols');
    var lineCount = (text.match(/\n/g) || []).length + 1;
    var wrappedLineCount = Math.ceil(text.length / cols);
    var totalLineCount = Math.max(lineCount, wrappedLineCount);
    $(this).attr('rows', totalLineCount);
});