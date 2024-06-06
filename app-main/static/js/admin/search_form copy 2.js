$(document).ready(function() {
    const pathsConfig = {
        searchBarUnitLimiter: {
            path: "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/adorganizationalunitlimiter/",
            setup: setupSearchBar
        },
        searchBarGroupAssociation: {
            path: "/admin/baAT5gt52eCRX7bu58msxF5XQtbY4bye/myview/adgroupassociation/",
            setup: setupSearchBar
        }
    };

    function setupSearchBar() {
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

            const distinguishedName = canonicalToDistinguishedName(canonicalName, false);
            console.log(distinguishedName); // Output the distinguished name for testing

            let formData = new FormData();
            formData.append('action', 'active_directory_query');
            formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
            formData.append('search_filter', `(&(objectClass=organizationalUnit)(distinguishedName=${distinguishedName}))`);
            formData.append('search_attributes', 'distinguishedName,canonicalName');
            formData.append('limit', '1');

            let response = await restAjax('POST', '/myview/ajax/', formData);
            if (!Array.isArray(response.data) || response.data.length !== 1) {
                alert(`Nothing found on\n\ncanonicalName: ${canonicalName}\ndistinguishedName: ${distinguishedName}`);
                return;
            }

            formData = new FormData();
            formData.append('action', 'ajax_search_form_add_new_organizational_unit');
            formData.append('organizational_unit', JSON.stringify(response.data));
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
    const regex = /^win\.dtu\.dk\/([a-zA-Z0-9]+\/?)*$/;
    return regex.test(canonicalName);
}

// function canonicalToDistinguishedName(canonicalName) {
//     let parts = canonicalName.split('/');
//     let domainParts = parts[0].split('.');
//     let organizationalUnits = parts.slice(1).reverse();

//     let distinguishedName = [];

//     // Add organizational units
//     organizationalUnits.forEach(ou => {
//         distinguishedName.push(`OU=${ou}`);
//     });

//     // Add domain components
//     domainParts.forEach(dc => {
//         distinguishedName.push(`DC=${dc}`);
//     });

//     return distinguishedName.join(',');
// }


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

    return distinguishedName.join(',');
}