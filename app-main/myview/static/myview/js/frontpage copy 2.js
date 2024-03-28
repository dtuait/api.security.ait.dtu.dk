console.log('Frontpage JS loaded');

// $('#syncAdUsersBtn').on('click', async function () {
//     const button = $(this);
//     const spinner = $('#loadingSpinner');

//     // Show the spinner and disable the button
//     spinner.show();
//     button.prop('disabled', true);

//     let response;
//     try {
//         // if (true || confirm("Are you sure you want to sync AD Users?")) {
//         if (true) {
//             const formData = new FormData();
//             formData.append('action', 'sync_ad_groups');
//             // response = await restAjax('POST', '/myview/ajax/', formData);
//             console.log('AD Groups Synced:', response);
//         }         
//     } catch (error) {
//         console.error('Error:', error);

//         // Optionally, show an error message to the user
//     } finally {
//         // Hide the spinner and enable the button
//         spinner.hide();
//         button.prop('disabled', false);
        
//         if (response.success) {
//             displayNotification('AD Groups synced successfully!', 'success');
//         } else if (response.error) {
//             displayNotification(response.error, 'warning');
//         } else {
//             displayNotification('An unknown error occurred.', 'warning');
//         }
//     }
// });




setModal(`#syncAdUsersBtn`, `syncAdUsersBtnModal`, {
    title: 'Sync AD Users',
    body: 'Are you sure you want to sync AD Users?',
    footer: `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-primary" id="confirmSyncAdUsersBtn">Sync</button>
    `,
    eventListeners: [
        {
            selector: '#confirmSyncAdUsersBtn',
            event: 'click',
            handler: async function () {
                const button = $(this);
                const modal = button.closest('.modal');
                const spinner = $('#loadingSpinner');
            
                // Show the spinner and disable the button
                spinner.show();
                button.prop('disabled', true);
            
                let response;
                try {                  
                    const modalElement = document.getElementById('syncAdUsersBtnModal');
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    modalInstance.hide();
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

                    // get the modal instance and hide it

                    if (response.status === 200) {
                        displayNotification('AD Groups synced successfully!', 'success');
                    } else if (response.error) {
                        displayNotification(response.error, 'warning');
                    } else {
                        displayNotification('An unknown error occurred.', 'warning');
                    }
                }
            }
        }
    ]	
});





