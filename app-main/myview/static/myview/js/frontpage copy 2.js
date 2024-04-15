console.log('Frontpage JS loaded');


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




async function createCustomToken() {
    // Create a new FormData object
    let formData = new FormData();

    // Append the 'action' parameter with the value 'create_custom_token'
    formData.append('action', 'create_custom_token');

    // Make the AJAX call
    let response = await restAjax('POST', '/myview/ajax/', formData);

    





    // Log the response
    console.log('Custom Token:', response.data);
}




setModal(`#generateTokenBtn`, `generateTokenBtnModal`, {
    title: 'Generate New Token',
    body: 'The token will only be displayed once, are you sure you want to generate a new token?',
    footer: `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-primary" id="confirmSyncAdUsersBtn">Generate New Token</button>
    `,
    eventListeners: [
        {
            selector: '#confirmSyncAdUsersBtn',
            event: 'click',
            handler: async function () {


            
            let formData = new FormData();     
            formData.append('action', 'create_custom_token');       
            
            let response;
            
            try {
                response = await restAjax('POST', '/myview/ajax/', formData);
                const modalElement = document.getElementById('generateTokenBtnModal');
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                modalInstance.hide();

            } catch (error) {
                console.log('Error:', error);
            } finally {
                if (response.status === 200) {
                    displayNotification('Token generated successfully!', 'success');
                    // Display the token in the modal
                    // <pre id="tokenDisplay" style="white-space: pre-wrap; word-wrap: break-word;">response.data.custom_token</pre>
                    let token = response.data.custom_token;
                    $('#tokenDisplay').text(token);
                    const tokenModalId = 'tokenDisplayModal';



                } else if (response.error) {
                    displayNotification(response.error, 'warning');
                } else {
                    displayNotification('An unknown error occurred.', 'warning');
                }
            }

            }
            
        },
    ]
})

setModal(`#confirmSyncAdUsersBtn`, `confirmSyncAdUsersBtnodal`, {
    title: 'Your New Token',
    body: 'The token will only be displayed once, are you sure you want to generate a new token?',
    footer: `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`,    
})

         


// $(document).ready(function() {
//     // Add a click event listener to the #copyTokenBtn button
//     $('#copyTokenBtn').click(function() {
//         // Create a new textarea element
//         let textarea = document.createElement('textarea');

//         // Set the value of the textarea to the text content of the #tokenDisplay element
//         textarea.value = $('#tokenDisplay').text();

//         // Append the textarea to the body
//         document.body.appendChild(textarea);

//         // Select the text in the textarea
//         textarea.select();

//         // Copy the text to the clipboard
//         document.execCommand('copy');

//         // Remove the textarea from the body
//         document.body.removeChild(textarea);

//         // Display a message to the user
//         alert('Token copied to clipboard');
//     });
// });


//     // Log the response
//     console.log('Custom Token:', response.data);

//                 const button = $(this);
//                 const modal = button.closest('.modal');
//                 const spinner = $('#loadingSpinner');
            
//                 // Show the spinner and disable the button
//                 spinner.show();
//                 button.prop('disabled', true);
            
//                 let response;
//                 try {                  
//                     const modalElement = document.getElementById('syncAdUsersBtnModal');
//                     const modalInstance = bootstrap.Modal.getInstance(modalElement);
//                     modalInstance.hide();
//                     const formData = new FormData();
//                     formData.append('action', 'sync_ad_groups');
//                     response = await restAjax('POST', '/myview/ajax/', formData);
//                     console.log('AD Groups Synced:', response);
                           
//                 } catch (error) {
//                     console.error('Error:', error);
            

//                     // Optionally, show an error message to the user
//                 } finally {
//                     // Hide the spinner and enable the button
//                     spinner.hide();
//                     button.prop('disabled', false);

//                     // get the modal instance and hide it

//                     if (response.status === 200) {
//                         displayNotification('AD Groups synced successfully!', 'success');
//                     } else if (response.error) {
//                         displayNotification(response.error, 'warning');
//                     } else {
//                         displayNotification('An unknown error occurred.', 'warning');
//                     }
//                 }
//             }
//         }
//     ]	
// });
