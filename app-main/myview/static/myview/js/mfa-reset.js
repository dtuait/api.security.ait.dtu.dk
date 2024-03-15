
x = 'mfa-reset JS loaded';
console.log(x);
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');

    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent the default form submission
        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            updateAuthenticationMethods(data);
        })
        .then((data) => {
            console.log('Form submitted');
        })
        .catch(error => console.error('Error:', error));
    });
});

function updateAuthenticationMethods(data) {


    // Assuming you want to create a copy of data and then modify that copy:
    const userPrincipalObj = data;
    const authenticationMethods = data.authentication_methods[0];  
    

    const container = document.querySelector('.container'); // Assuming you want to append the list here
    
    // Start building HTML content for userPrincipalObj
    
    let htmlContent = '<div class="user-principal-info">';
    let elementInfo = document.querySelector('.user-principal-info');
    if (elementInfo) {
        elementInfo.remove();
    }
    const fields = ['displayName', 'givenName', 'id', 'jobTitle', 'mail', 'mobilePhone', 'officeLocation', 'surname', 'userPrincipalName'];

    for (const field of fields) {
        const value = userPrincipalObj[field];
        if (value !== undefined) {
            // Handle array values differently to concatenate their contents
            if (Array.isArray(value)) {
                htmlContent += `<div><strong>${field}:</strong> ${value.join(', ')}</div>`;
            } else {
                htmlContent += `<div><strong>${field}:</strong> ${value}</div>`;
            }
        }
    }
    htmlContent += '</div>'; // Close the user principal info div

    // Continue with building HTML content for authentication methods
    htmlContent += '<div class="auth-methods-list">';
    let elementAuth = document.querySelector('.auth-methods-list');
    if (elementAuth) {
        elementAuth.remove();
    }
    authenticationMethods.value.forEach(method => {
        let methodDiv = '<div class="auth-method my-4">';
        for (const [key, value] of Object.entries(method)) {
            // if (key !== '@odata.type') { // Skip the @odata.type property
                methodDiv += `<span><strong>${key}:</strong> ${value}</span><br>`;
            // }
        }

        // only add button if the @odata.type property contains '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod'
        if (method['@odata.type'] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod') {
            methodDiv += `<button class="btn btn-danger remove-btn" data-method-id="${method.id}">Remove</button>`;
        } else {
            methodDiv += `<button type="button" class="btn btn-info" data-bs-toggle="modal" data-bs-target="#infoModal">Info</button>`;
        }

        methodDiv += '</div>';
        htmlContent += methodDiv;
    });
    htmlContent += '</div>'; // Close the auth methods list div

    // container.innerHTML += htmlContent; // Replace the container's content
    container.insertAdjacentHTML('beforeend', htmlContent); // Append the new HTML
}





// function updateAuthenticationMethods(data) {

//     const authenticationMethods = data.authenticationMethods;
//     const userPrincipalObj = data



//     const container = document.querySelector('.container'); // Assuming you want to append the list here
//     let htmlContent = '<div class="auth-methods-list">';


//     authenticationMethods[0].value.forEach(method => {
//         // Start the div for this auth method
//         let methodDiv = `<div class="auth-method">`;
    
//         // Add a span for each property in the method, except for '@odata.type'
//         for (const [key, value] of Object.entries(method)) {
//             if (key !== '@odata.type') { // Skip the @odata.type property
//                 methodDiv += `<span><strong>${key}:</strong> ${value}</span><br>`;
//             }
//         }
    
//         // Add the remove button with the method's ID
//         methodDiv += `<button class="btn btn-danger remove-btn" data-method-id="${method.id}">Remove</button>`;
    
//         // Close the div
//         methodDiv += `</div>`;
    
//         // Append this method's div to the overall HTML content
//         htmlContent += methodDiv;
//     });

//     htmlContent += '</div>';
//     container.innerHTML += htmlContent; // Append the new HTML
// }