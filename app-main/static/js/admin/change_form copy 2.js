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
                    let formData = new FormData();
                    formData.append('action', 'active_directory_query');
                    formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
                    formData.append('search_filter', `(&(objectClass=group)(cn=*${this.value}*))`);
                    formData.append('search_attributes', 'cn,canonicalName,distinguishedName');
                    formData.append('limit', '1');
            
                    let response;
                    response = await restAjax('POST', '/myview/ajax/', formData);
            
                    console.log('Response:', response);

                    let ad_groups = response.data;

                    // for each group in ad_groups print the group name
                    for (let i = 0; i < ad_groups.length; i++) {
                        // print cn, canonicalName, distinguishedName
                        console.log(ad_groups[i].cn, ad_groups[i].canonicalName, ad_groups[i].distinguishedName);
                    }

                    // Assuming `id_ad_groups_from` is the select element for ad_groups
                    let selectElement = $('#id_ad_groups_from');

                    // Clear existing options
                    selectElement.empty();

                    // Add new options based on AJAX response
                    ad_groups.forEach(group => {
                        let option = new Option(group.cn, group.distinguishedName); // Assuming distinguishedName is the value you store in the database
                        selectElement.append($(option));
                    });
                                        // Clear the timeout
                    timeout = null;
                }.bind(this), 2000);  // Wait for 2 seconds
            });

        }
    }, 100); // check every 100ms
});



// // id_ad_groups_from
// let id_ad_groups_from;

// $(document).ready(function() {
//     let checkExist = setInterval(function() {
//         let input = $('#id_ad_groups_from');

//         console.log('Input exists!', input);

//         // Clear existing options
//         input.empty();

            
//         clearInterval(checkExist);  // Clear interval once we've found the input
//         id_ad_groups_from = input;
//     }, 100); // check every 100ms
// });





// Add your JavaScript code here
// document.addEventListener('DOMContentLoaded', function () {
//     const filterInput = document.querySelector('selector for your filter input'); // Replace with the actual selector for the filter input

//     if (filterInput) {

//         filterInput.addEventListener('input', function () {
//             // Throttle this if necessary to avoid too many AJAX calls
//             const searchTerm = this.value;
//             fetch(`/path-to-your-custom-view/?term=${encodeURIComponent(searchTerm)}`)
//                 .then(response => response.json())
//                 .then(data => {
//                     // Process and update your filter select options with data
//                 })
//                 .catch(error => console.error('Error:', error));
//         });
//     }
// });
