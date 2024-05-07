$(document).ready(function() {

    // Monitor the fields specifically for the change form endpoint
    let endpointChangeFormMonitor = setInterval(function() {
        let inputGroup = $('#id_ad_groups_input');
        // let inputOrganizationalUnit = $('#id_ad_organizational_units_input');
        let currentPath = window.location.pathname;
        let formattedPath = currentPath.replace(/\/(\d+)\//, '/x/');

        // Check if path matches exactly the required change form path
        const requiredPath = "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/endpoint/x/change/";
        if (formattedPath === requiredPath && inputGroup) {
            clearInterval(endpointChangeFormMonitor); // Stop monitoring once the path and elements are confirmed

            let timeoutId = null;
            inputGroup.on('input', function() {
                if (timeoutId !== null) {
                    clearTimeout(timeoutId);
                }
                timeoutId = setTimeout(async function() {
                    if (!this.value) return; // Guard clause for empty input
    
                    let formData = new FormData();
                    formData.append('action', 'active_directory_query');
                    formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
                    formData.append('search_filter', `(&(objectClass=group)(cn=*${this.value}*))`);
                    formData.append('search_attributes', 'cn,canonicalName,distinguishedName');
                    formData.append('limit', '100');
    
                    let response = await restAjax('POST', '/myview/ajax/', formData);
                    console.log('Response:', response);
    
                    formData = new FormData();
                    formData.append('action', `ajax_change_form_update_form_ad_groups`);
                    formData.append(`ad_groups`, JSON.stringify(response.data));
                    formData.append('path', window.location.pathname);
                    response = await restAjax('POST', '/myview/ajax/', formData);
                    console.log('Reloading page...');
                    location.reload();
                    timeoutId = null;
                }.bind(this), 2000);
            });
        } else {
            clearInterval(endpointChangeFormMonitor); // Stop monitoring if path does not match
        }
    }, 100); // check every 100ms


    // Placeholder for the second monitor function if required
    let anotherPathMonitor = setInterval(function() {

        // http://localhost:6081/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/adorganizationalunitlimiter/
        // element id = searchbar
        // on input console.log(searchbar input text)
    }, 100);
});
