console.log('Hello from change_form.js');

$(document).ready(function() {
    let checkExist = setInterval(function() {
        let input = $('#id_ad_groups_input');
        if (input) {
            
            console.log('Input exists!', input);
            
            clearInterval(checkExist);  // Clear interval once we've found the input
            // Attach your event listener here
            let timeout = null;

            input.on('input', function() {
                // Clear the previous timeout if it exists
                if (timeout !== null) {
                    clearTimeout(timeout);
                }
            
                // Set a new timeout
                timeout = setTimeout(async function() {
                    // only run if the input is not empty
                    if (this.value === '' || this.value === null || this.value === undefined) {
                        return;
                    }

                    let formData = new FormData();
                    formData.append('action', 'active_directory_query');
                    formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
                    formData.append('search_filter', `(&(objectClass=group)(cn=*${this.value}*))`);
                    formData.append('search_attributes', 'cn,canonicalName,distinguishedName');
                    formData.append('limit', '100');
            
                    let response;
                    response = await restAjax('POST', '/myview/ajax/', formData);
            
                    console.log('Response:', response);

                    let ad_groups = response.data;

                    // for each group in ad_groups print the group name
                    // for (let i = 0; i < ad_groups.length; i++) {
                    //     // print cn, canonicalName, distinguishedName
                    //     console.log(ad_groups[i].cn, ad_groups[i].canonicalName, ad_groups[i].distinguishedName);
                    // }

                    // Assuming `id_ad_groups_from` is the select element for ad_groups
                    let selectElement = $('#id_ad_groups_from');
                    // 

                    // Clear existing options
                    // selectElement.empty();

                    // Add new options based on AJAX response
                    ad_groups.forEach(group => {
                        let option = new Option(group.cn, group.cn); // Set both the display text and the value to group.cn
                        option.setAttribute('title', group.distinguishedName); // Use distinguishedName as the title, if necessary
                        selectElement.append(option);
                    });

                    // empty formData as new formData will be created in the next iteration

                    formData = null;
                    formData = new FormData();
                    formData.append('action', 'ajax_change_form_update_form_ad_groups');
                    formData.append('ad_groups', JSON.stringify(ad_groups));
                    formData.append('path', window.location.pathname);
                    response = await restAjax('POST', '/myview/ajax/', formData);



                    // how can i reload the page
                    console.log('Reloading page...');

                    // PARSE THE DATA AND RELOAD THE PAGE
                    location.reload();

                                        // Clear the timeout
                    timeout = null;
                }.bind(this), 2000);  // Wait for 2 seconds
            });

        }
    }, 100); // check every 100ms
});



// $(document).ready(function() {
//     let checkExist = setInterval(function() {
//         let input = $('#id_ad_groups_input');
//         if (input.length) { // Ensure the element exists
//             console.log('Input exists!');
//             clearInterval(checkExist); // Clear interval once we've found the input
            
//             // Initialize a timeout variable
//             let timeout = null;

//             // Event listener for input changes
//             input.on('input', function() {
//                 // Clear the previous timeout if it exists
//                 if (timeout !== null) {
//                     clearTimeout(timeout);
//                 }
                
//                 // Set a new timeout
//                 timeout = setTimeout(function() {
//                     let formData = new FormData();
//                     formData.append('action', 'active_directory_query');
//                     formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
//                     formData.append('search_filter', `(&(objectClass=group)(cn=*${this.value}*))`);
//                     formData.append('search_attributes', 'cn,canonicalName,distinguishedName');
//                     formData.append('limit', '1');

//                     // Replace 'restAjax' and URL with your actual AJAX request function and endpoint
//                     $.ajax({
//                         type: 'POST',
//                         url: '/myview/ajax/', // Your server endpoint
//                         data: formData,
//                         contentType: false,
//                         processData: false,
//                         success: function(response) {
//                             console.log('Response:', response);
//                             let ad_groups = response.data;
//                             let selectElement = $('#id_ad_groups_from');
                            
//                             // Clear existing options
//                             selectElement.empty();

//                             // Add new options based on AJAX response
//                             ad_groups.forEach(group => {
//                                 let option = new Option(group.cn, group.distinguishedName); // Assuming distinguishedName is the value
//                                 selectElement.append($(option));
//                             });
//                         },
//                         error: function(xhr, status, error) {
//                             console.error('Error:', error);
//                         }
//                     });

//                     // Clear the timeout
//                     timeout = null;
//                 }.bind(input), 2000); // Wait for 2 seconds
//             });

//         }
//     }, 100); // Check every 100ms
// });



// console.log('Hello from change_form.js');

// $(document).ready(function() {
//     let checkExist = setInterval(function() {
//         let input = $('#id_ad_groups_input');
//         if (input.length > 0) {  // Ensuring the input element is found
//             console.log('Input exists!', input);
            
//             clearInterval(checkExist);  // Stop checking once the input is found

//             // Function to handle debounced input
//             let handleInput = function() {
//                 let value = input.val(); // Get current value of input

//                 // Prepare data for restAjax call
//                 let data = {
//                     action: 'active_directory_query',
//                     base_dn: 'DC=win,DC=dtu,DC=dk',
//                     search_filter: `(&(objectClass=group)(cn=*${value}*))`,
//                     search_attributes: 'cn,canonicalName,distinguishedName',
//                     limit: '1'
//                 };

//                 // Use your custom restAjax function
//                 response = await restAjax('POST', '/myview/ajax/', formData);


//                 console.log('Response:', response);

//                 let ad_groups = response.data;


//                 let selectElement = $('#id_ad_groups_from');

//                 // Clear existing options
//                 selectElement.empty();

//                 // Add new options based on AJAX response
//                 ad_groups.forEach(group => {
//                     let option = new Option(group.cn, group.distinguishedName); // Assuming distinguishedName is the value you store in the database
//                     selectElement.append($(option));
//                 });


//             // Setup debounce mechanism
//             let timeout = null;
//             input.on('input', function() {
//                 // Clear the previous timeout if it exists
//                 if (timeout !== null) {
//                     clearTimeout(timeout);
//                 }

//                 // Set a new timeout to debounce the input
//                 timeout = setTimeout(handleInput, 2000);  // Wait for 2 seconds after the user has stopped typing
//             });
//         }
// });
