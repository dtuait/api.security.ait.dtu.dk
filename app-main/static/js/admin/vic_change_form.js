$(document).ready(function() {
    // Monitor the fields specifically for the change form endpoint
    let endpointChangeFormMonitor = setInterval(function() {
        let inputGroup = $('#id_ad_groups_input');
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
                    formData.append('limit', '5');
    
                    let response = await restAjax('POST', '/myview/ajax/', formData);
                    console.log('Response:', response);
    
                    formData = new FormData();
                    formData.append('action', 'ajax_change_form_update_form_ad_groups');
                    formData.append('ad_groups', JSON.stringify(response.data));
                    formData.append('path', window.location.pathname);
                    response = await restAjax('POST', '/myview/ajax/', formData);
                    console.log('Reloading page...');
                    location.reload();
                    timeoutId = null;
                }.bind(this), 500);
            });
        } else {
            clearInterval(endpointChangeFormMonitor); // Stop monitoring if path does not match
        }
    }, 100); // check every 100ms

    // Monitor inputs on another path for the organizational unit limiter endpoint
    let anotherPathMonitor = setInterval(function() {
        let searchBar = $('#searchbar');
        let currentPath = window.location.pathname;

        const requiredPathForSearchBar = "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/adorganizationalunitlimiter/";
        if (currentPath === requiredPathForSearchBar && searchBar) {
            clearInterval(anotherPathMonitor); // Stop monitoring once the path and element are confirmed

            searchBar.on('input', function() {
                console.log('Searchbar input text:', this.value);
            });
        } else {
            clearInterval(anotherPathMonitor); // Stop monitoring if path does not match
        }
    }, 100);
});
