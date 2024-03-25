console.log('Frontpage JS loaded');

$('#syncAdUsersBtn').on('click', async function () {
    const button = $(this);
    const spinner = $('#loadingSpinner');

    // Show the spinner and disable the button
    spinner.show();
    button.prop('disabled', true);

    let response;
    try {
        const formData = new FormData();
        formData.append('action', 'sync_ad_groups');
        response = await restAjax('POST', '/myview/ajax/', formData);
        console.log('AD Groups Synced:', response);
    } catch (error) {
        console.error('Error:', error);

        // Optionally, show an error message to the user
    } finally {
        // Hide the spinner and enable the button
        spinner.hide();
        button.prop('disabled', false);
        
        if (response.success) {
            displayNotification('AD Groups synced successfully!', 'success');
        } else if (response.error) {
            displayNotification(response.error, 'warning');
        } else {
            displayNotification('An unknown error occurred.', 'warning');
        }
    }
});






