$(document).ready(function() {
    const pathsConfig = {
        searchBarUnitLimiter: {
            path: "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/adorganizationalunitlimiter/",
            setup: setupSearchBarForUnitLimiter
        },
        searchBarGroupAssociation: {
            path: "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/adgroupassociation/",
            setup: setupSearchBarForGroupAssociation
        }
    };


    const ENDS_WITH_A_COMMON_NAME = true;



















    function setupSearchBarForUnitLimiter() {
        const searchBar = $('#searchbar');

        // Display expansion glass
        $('#vicre-search-and-find-by-canonicalname-searchbar').css('display', 'inline-block');
        $('#django-vanilla-searchbar').hide();
        

        searchBar.on('input', function() {
            const input = $(this);
            const isValid = isValidCanonicalName(input.val());
            const currentTheme = localStorage.getItem("theme") || "dark";
            


            if (!input.val()) {
                // Reset to default background color if input is empty
                input.css('backgroundColor', '');
            } else if (isValid) {
                // Set background color to light green if the input is a valid canonical name
                input.css('backgroundColor', 'lightgreen');
            } else {
                // Set background color to light red if the input is not a valid canonical name
                input.css('backgroundColor', 'lightcoral');
            }
        });

        const form = document.querySelector('#changelist-search');


        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            const input = this.querySelector('input[type="text"]');
            const canonicalName = input.value;

            if (!input.value || !isValidCanonicalName(canonicalName)) {
                alert('Please enter a valid canonical name.');
                return;
            } // Guard clause for empty input

            // const IS_NOT_A_COMMOMNAME = false;
            const distinguishedName = canonicalToDistinguishedName(canonicalName, !ENDS_WITH_A_COMMON_NAME);
            console.log(distinguishedName); // Output the distinguished name for testing






            formData = new FormData();
            formData.append('action', 'ajax__search_form__add_new_organizational_unit');
            formData.append('distinguished_name', distinguishedName);
            response = await restAjax('POST', '/myview/ajax/', formData);
            
            console.log(response.data);

            


            // let response = await restAjax('POST', '/myview/ajax/', formData);
            // if (!Array.isArray(response.data) || response.data.length !== 1) {
            //     console.log(`Nothing found on\n\ncanonicalName: ${canonicalName}\ndistinguishedName: ${distinguishedName}`)
            //     alert(`Nothing found on\n\ncanonicalName: ${canonicalName}\ndistinguishedName: ${distinguishedName}`);
            //     return;
            // }
        });
    }



























    function setupSearchBarForGroupAssociation() {
        const searchBar = $('#searchbar');

        // Display expansion glass
        $('#vicre-search-and-find-by-canonicalname-searchbar').css('display', 'inline-block');
        $('#django-vanilla-searchbar').hide();

        searchBar.on('input', function() {
            const input = $(this);
            const isValid = isValidCanonicalName(input.val());

            if (!input.val()) {
                // Reset to default background color if input is empty
                input.css('backgroundColor', '');
            } else if (isValid) {
                // Set background color to light green if the input is a valid canonical name
                input.css('backgroundColor', 'lightgreen');
            } else {
                // Set background color to light red if the input is not a valid canonical name
                input.css('backgroundColor', 'lightcoral');
            }
        });

        const form = document.querySelector('#changelist-search');


        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            const input = this.querySelector('input[type="text"]');
            const canonicalName = input.value;

            if (!input.value || !isValidCanonicalName(canonicalName)) {
                alert('Please enter a valid canonical name.');
                return;
            } // Guard clause for empty input


            const distinguishedName = canonicalToDistinguishedName(canonicalName, ENDS_WITH_A_COMMON_NAME);
            console.log(distinguishedName); // Output the distinguished name for testing

            let formData = new FormData();
            formData.append('action', 'active_directory_query');
            formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
            formData.append('search_filter', `(&(objectClass=group)(distinguishedName=${distinguishedName}))`);
            formData.append('search_attributes', 'distinguishedName,canonicalName');
            formData.append('limit', '1');

            let response = await restAjax('POST', '/myview/ajax/', formData);
            if (!Array.isArray(response.data) || response.data.length !== 1) {
                alert(`Nothing found on\n\ncanonicalName: ${canonicalName}\ndistinguishedName: ${distinguishedName}`);
                location.reload();
            }

            formData = new FormData();
            formData.append('action', 'ajax_change_form_update_form_ad_groups');
            formData.append('ad_groups', JSON.stringify(response.data));
            response = await restAjax('POST', '/myview/ajax/', formData);
            console.log('Reloading page...');
            location.reload();
        });
    }









    function monitorPaths() {
        const currentPath = window.location.pathname;
        const pathConfig = Object.values(pathsConfig).find(config => config.path === currentPath);

        if (pathConfig && pathConfig.setup) {
            pathConfig.setup();
        }
    }

    monitorPaths();
});




































function isValidCanonicalName(canonicalName) {
    const regex = /^win\.dtu\.dk\/([a-zA-Z0-9\s\-]+\/?)*$/;
    const isValidCanonicalName = regex.test(canonicalName);
    return isValidCanonicalName;
}



function canonicalToDistinguishedName(canonicalName, endsWithCommonName) {
    let parts = canonicalName.split('/');
    let domainParts = parts[0].split('.');
    let organizationalUnits = parts.slice(1).reverse();

    let distinguishedName = [];

    // Add organizational units
    organizationalUnits.forEach((ou, index) => {
        if (endsWithCommonName && index === 0) {
            distinguishedName.push(`CN=${ou}`);
        } else {
            distinguishedName.push(`OU=${ou}`);
        }
    });

    // Add domain components
    domainParts.forEach(dc => {
        distinguishedName.push(`DC=${dc}`);
    });

    const distinguishedNameString = distinguishedName.join(',');

    return distinguishedNameString
}
