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
        
            // Define colors for dark and light modes
            const colors = {
                dark: {
                    valid: '#006400', // Dark green
                    invalid: '#8B0000', // Dark red
                    defaultBg: '#333333', // Dark gray
                    textColor: '#FFFFFF' // White text
                },
                light: {
                    valid: '#90EE90', // Light green
                    invalid: '#FFB6C1', // Light red
                    defaultBg: '#FFFFFF', // White
                    textColor: '#000000' // Black text
                }
            };
        
            const themeColors = colors[currentTheme];
        
            if (!input.val()) {
                // Reset to default background color if input is empty
                input.css('backgroundColor', themeColors.defaultBg);
                input.css('color', themeColors.textColor);
            } else if (isValid) {
                // Set background color to green if the input is a valid canonical name
                input.css('backgroundColor', themeColors.valid);
                input.css('color', themeColors.textColor);
            } else {
                // Set background color to red if the input is not a valid canonical name
                input.css('backgroundColor', themeColors.invalid);
                input.css('color', themeColors.textColor);
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

            const distinguishedName = canonicalToDistinguishedName(canonicalName, !ENDS_WITH_A_COMMON_NAME);
            console.log(distinguishedName); // Output the distinguished name for testing






            formData = new FormData();
            formData.append('action', 'ajax__search_form__add_new_organizational_unit');
            formData.append('distinguished_name', distinguishedName);
            try {

                const response = await restAjax('POST', '/myview/ajax/', formData);

                if (response.status === 200) {
                    // Handle 200 OK status
                    console.log('Success: ', response);
                } else if (response.status === 201) {
                    // Handle 201 Created status
                    console.log('Created: ', response);
                    location.reload();
                } else if (response.status === 500) {
                    // Handle 500 Internal Server Error status
                    console.error('Server error: ', response);
                    alert(`Server error: ${response.data.error}`);

                } else {
                    // Handle other statuses
                    console.log('Other status: ', response);
                }
            } catch (error) {
                // Handle any errors that occurred during the execution of the restAjax function
                console.error('An error occurred: ', error);
            }

        
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
            const currentTheme = localStorage.getItem("theme") || "dark";
        
            // Define colors for dark and light modes
            const colors = {
                dark: {
                    valid: '#006400', // Dark green
                    invalid: '#8B0000', // Dark red
                    defaultBg: '#333333', // Dark gray
                    textColor: '#FFFFFF' // White text
                },
                light: {
                    valid: '#90EE90', // Light green
                    invalid: '#FFB6C1', // Light red
                    defaultBg: '#FFFFFF', // White
                    textColor: '#000000' // Black text
                }
            };
        
            const themeColors = colors[currentTheme];
        
            if (!input.val()) {
                // Reset to default background color if input is empty
                input.css('backgroundColor', themeColors.defaultBg);
                input.css('color', themeColors.textColor);
            } else if (isValid) {
                // Set background color to green if the input is a valid canonical name
                input.css('backgroundColor', themeColors.valid);
                input.css('color', themeColors.textColor);
            } else {
                // Set background color to red if the input is not a valid canonical name
                input.css('backgroundColor', themeColors.invalid);
                input.css('color', themeColors.textColor);
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
            formData = new FormData();
            formData.append('action', 'ajax__search_form__add_new_ad_group_associations');
            formData.append('distinguished_name', distinguishedName);
            try {

                const response = await restAjax('POST', '/myview/ajax/', formData);

                if (response.status === 200) {
                    // Handle 200 OK status
                    console.log('Success: ', response);
                } else if (response.status === 201) {
                    // Handle 201 Created status
                    console.log('Created: ', response);
                    location.reload();
                } else if (response.status === 500) {
                    // Handle 500 Internal Server Error status
                    console.error('Server error: ', response);
                    alert(`Server error: ${response.data.error}`);
                } else {
                    // Handle other statuses
                    console.log('Other status: ', response);
                }
            } catch (error) {
                // Handle any errors that occurred during the execution of the restAjax function
                console.error('An error occurred: ', error);
            }
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
