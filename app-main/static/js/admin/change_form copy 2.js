console.log('Hello from change_form.js');

$(document).ready(function() {




    let checkExist = setInterval(function() {

        let inputGroup  = $('#id_ad_groups_input');
        let inputOU     = $('#id_ad_organizational_units_input');
        if (inputGroup && inputOU) {
            
            // input 
            console.log('Input exists!', inputGroup);
            console.log('Input exists!', inputOU);
            
            clearInterval(checkExist);  // Clear interval once we've found the input
            
            
            
            
            
            
            
            
            
            
            
            
            
            // Attach your event listener here
            let timeoutGroup = null;
            inputGroup.on('input', function() {
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
            
                    console.log('Response:', response);

                    let ad_groups = response.data;

                    // Assuming `id_ad_groups_from` is the select element for ad_groups
                    let selectElement = $('#id_ad_groups_from');
    
                    // Add new options based on AJAX response
                    ad_groups.forEach(group => {
                        let option = new Option(group.cn, group.cn); // Set both the display text and the value to group.cn
                        option.setAttribute('title', group.distinguishedName); // Use distinguishedName as the title, if necessary
                        selectElement.append(option);
                    });

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
            inputOU.on('input', function () {
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
                    console.log("Hello world");
                    // Clear the timeoutGroup
                    timeoutGroup = null;
                }.bind(this), 2000);  // Wait for 2 seconds
            })

        }







    }, 100); // check every 100ms






    

});



