$(document).ready(function() {



    // Detect the fields
    let checkExist1 = setInterval(function() {

        // this is for http://localhost:6081/admin//myview/endpoint/
        let inputGroupEndpoint  = $('#id_ad_groups_input');
        let inputOUEndpoint     = $('#id_ad_organizational_units_input');
        let path = window.location.pathname;
        let EndpointChangeFormPath = path.replace(/\/(\d+)\//, '/x/'); // >> '/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/endpoint/x/change/'
        
        // if newPath is not equal /admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/endpoint/x/change/ then clearInterval without setting a function





        if (inputGroupEndpoint && inputOUEndpoint && EndpointChangeFormPath === "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/endpoint/x/change/") {
            
            clearInterval(checkExist1);  // Clear interval once we've found the input
            
            // Attach your event listener here
            let timeoutGroup = null;
            inputGroupEndpoint.on('input', function() {
                // Clear the previous timeoutGroup if it exists
                if (timeoutGroup !== null) {
                    clearTimeout(timeoutGroup);
                }
            
                // Set a new timeout
                timeoutGroup = setTimeout(async function() {
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
                    // console.log('Response:', response);

                    let ad_groups = response.data;
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

                    // Clear the timeoutGroup
                    timeoutGroup = null;
                }.bind(this), 2000);  // Wait for 2 seconds
            });


            let timeoutOU = null;
            inputOUEndpoint.on('input', function () {
                // Clear the previous timeoutGroup if it exists
                if (timeoutOU !== null) {
                    clearTimeout(timeoutOU);
                }
            
                // Set a new timeout
                timeoutOU = setTimeout(async function() {
                    // only run if the input is not empty
                    if (this.value === '' || this.value === null || this.value === undefined) {
                        return;
                    }

                    let formData = new FormData();
                    formData.append('action', 'active_directory_query');
                    formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
                    formData.append('search_filter', `(&(objectClass=organizationalUnit)(ou=*${this.value}*))`); // Modified for OU
                    formData.append('search_attributes', 'distinguishedName');
                    formData.append('limit', '100');

                    let response;
                    response = await restAjax('POST', '/myview/ajax/', formData);

                    console.log('Response:', response);

                    let ad_ous = response.data;

                    // Send the data to the server
                    formData = new FormData();
                    formData.append('action', 'ajax_change_form_update_form_ad_ous');
                    formData.append('ad_ous', JSON.stringify(ad_ous));
                    formData.append('path', window.location.pathname);
                    response = await restAjax('POST', '/myview/ajax/', formData);

                    // how can i reload the page
                    console.log('Reloading page...');

                    // PARSE THE DATA AND RELOAD THE PAGE
                    location.reload();

                    // Clear the timeoutGroup
                    timeoutGroup = null;
                }.bind(this), 2000);  // Wait for 2 seconds
            })

        } else if (EndpointChangeFormPath !== "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/endpoint/x/change/") {
            clearInterval(checkExist1);
        }

    }, 100); // check every 100ms



    let checkExist2 = setInterval(function() {
        // Code for second interval

    }, 100);
    



    

});



