console.log('Hello from change_form.js');

$(document).ready(function() {
    let checkExist = setInterval(function() {
        let input = $('#id_ad_groups_input');
        if (input) {
            
            console.log('Input exists!', input);
            
            clearInterval(checkExist);  // Clear interval once we've found the input
            // Attach your event listener here
            input.on('input', async function() {
                


                console.log('Input changed!', this.value);

                let formData = new FormData();
                formData.append('action', 'active_directory_query');
                // Append additional parameters required by the Django view
                formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
                // search_filter = '(objectClass=group)(cn=*' + this.value )'
                // formData.append('search_filter', search_filter);
                // formData.append('search_filter', `(objectClass=group)(cn=${this.value})`);
                formData.append('search_filter', `(objectClass=group)(cn=*${this.value}*)`);

                formData.append('search_attributes', 'distinguishedName,sAMAccountName');
                formData.append('limit', '5');

                let response;
                response = await restAjax('POST', '/myview/ajax/', formData);

                console.log('Response:', response);


            });

        }
    }, 100); // check every 100ms
});



// id_ad_groups_from
let id_ad_groups_from;

$(document).ready(function() {
    let checkExist = setInterval(function() {
        let input = $('#id_ad_groups_from');

        console.log('Input exists!', input);

            
        clearInterval(checkExist);  // Clear interval once we've found the input
        id_ad_groups_from = input;
    }, 100); // check every 100ms
});





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
