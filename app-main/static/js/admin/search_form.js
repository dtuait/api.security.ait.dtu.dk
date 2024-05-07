$(document).ready(function() {
     // Monitor inputs on another path for the organizational unit limiter endpoint
    let anotherPathMonitor = setInterval(function() {
        let searchBar = $('#searchbar');
        let currentPath = window.location.pathname;

        const requiredPathForSearchBar = "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/adorganizationalunitlimiter/";
        if (currentPath === requiredPathForSearchBar && searchBar) {
            clearInterval(anotherPathMonitor); // Stop monitoring once the path and element are confirmed

            let form = document.querySelector('#changelist-search');
            form.addEventListener('submit', async function(event) {
                event.preventDefault();
            
                let input = this.querySelector('input[type="text"]');
                if (!input.value) return; // Guard clause for empty input
            
                let formData = new FormData();
                formData.append('action', 'active_directory_query');
                formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
                formData.append('search_filter', `(&(objectClass=organizationalUnit)(distinguishedName=${input.value}))`);
                formData.append('search_attributes', 'distinguishedName,canonicalName');
                formData.append('limit', '1');
            
                let response = await restAjax('POST', '/myview/ajax/', formData);
                console.log('Response:', response);
            
                formData = new FormData();
                formData.append('action', 'ajax_search_form_add_new_organizational_unit');
                formData.append('organizational_unit', JSON.stringify(response.data));
                response = await restAjax('POST', '/myview/ajax/', formData);
                console.log('Reloading page...');
                location.reload();
            });


        } else {
            clearInterval(anotherPathMonitor); // Stop monitoring if path does not match
        }
    }, 100);
});
