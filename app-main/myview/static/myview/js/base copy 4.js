// // Confirm that cash are loaded
// console.log(`base.js: ${confirmCash()}`);

// // Confirm that axios are loaded
// confirmAxios().then(response => {
//   console.log(response);
// }).catch(error => {
//   console.error(error);
// });

// // confirm that qs are loaded
// console.log(`qs: ${Qs}`);




/**
 * Perform a REST AJAX request.
 * @param {string} method - The HTTP method ('GET', 'POST', 'DELETE', etc.)
 * @param {string} url - The URL endpoint.
 * @param {Object|FormData} data - The data to be sent. Pass an object for JSON, FormData for form data.
 * @param {Object} headers - Optional. Additional headers to send.
 */
async function restAjax(method, url, data = {}, headers = {}) {
  
  let response;
  try {
    // Determine if the data is FormData or JSON, and adjust headers accordingly
    const isFormData = data instanceof FormData;
    if (!isFormData && !(data instanceof URLSearchParams)) {
      // Assume JSON if not FormData or URLSearchParams
      data = JSON.stringify(data);
      headers['Content-Type'] = 'application/json';
    }

    // Add CSRF token for Django compatibility
    const csrfToken = document.cookie.match(/csrftoken=([\w-]+)/)?.[1];
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;

    // Perform the request using Axios
    response = await axios({
      method: method,
      url: url,
      data: isFormData ? data : Qs.stringify(data),
      headers: headers,
      withCredentials: true,
    });

    // Handle response
    console.log('Response:', response.data);
    // return response.data;
  } catch (error) {
    return error.response.data;
    console.error('AJAX request failed:', error);
    throw error; // Re-throw to let the caller handle it
  } finally
  {
    // Perform any cleanup tasks here
    return response.data;
  }

}




function printCurlCommand(url, csrfToken, formData) {
  let dataString = new URLSearchParams(formData).toString();
  let command = `curl -X POST '${url}' -H 'Content-Type: application/x-www-form-urlencoded' -H 'X-CSRFToken: ${csrfToken}' -d '${dataString}' -b cookies.txt`;
  console.log(command);
}

function displayNotification(message, type) {
  const alertType = type === 'success' ? 'alert-success' : 'alert-warning';
  const notificationHtml = `<div class="alert ${alertType} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  </div>`;

  const notificationsContainer = document.getElementById('notifications-container');
  notificationsContainer.innerHTML = notificationHtml; // Add the notification to the container
}




function updateSessionStorage(data, prefix) {
  // example updateSessionStorage({userPrincipalObj: data}, 'myApp');

  // Iterate over each key-value pair in the data object
  for (let key in data) {
    if (data.hasOwnProperty(key)) {
      // Convert the data to a JSON string
      let jsonData = JSON.stringify(data[key]);

      // Save the data to session storage with a unique key
      sessionStorage.setItem(`${prefix}-${key}`, jsonData);
    }
  }
}


/**
 * Dynamically creates and attaches a modal to a trigger element.
 * 
 * @param {string} triggerSelector - Selector for the element that triggers the modal.
 * @param {string} modalId - Unique ID for the modal.
 * @param {Object} options - Optional settings for modal customization.
 */
function setModal(triggerSelector, modalId, options = {}) {
  // this function assumes that each that a mudal is uniqie to a trigger


  if ($('#' + modalId).length) {
    $('#' + modalId).remove();
  }

  // if options are provided, use them to update the modal

  const modalType = options.modalType || 'modal-dialog'
  const modalContent = options.modalContent || 'modal-content';
  const modalTitle = options.title || 'Default Modal Title';
  const modalBody = options.body || 'Default Modal Body';
  const modalFooter = options.footer || `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`;


  // Create the modal HTML with the provided content and a unique ID
  const modalHtml = `
      <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
          <div class="${modalType}">
              <div class="${modalContent}">
                  <div class="modal-header">
                      <h5 class="modal-title" id="${modalId}Label">${modalTitle}</h5>
                      <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <div class="modal-body">
                      ${modalBody}
                  </div>
                  <div class="modal-footer">
                      ${modalFooter}
                  </div>
              </div>
          </div>
      </div>
  `;

  // Append the modal to the body
  $('body').append(modalHtml);

  // Use Bootstrap to handle the modal
  const modalInstance = new bootstrap.Modal(document.getElementById(modalId), {
    keyboard: false
  });

  // Detach existing click events to prevent multiple bindings
  $(triggerSelector).off('click').on('click', function () {
    console.log('Trigger clicked');
    modalInstance.show();
  });

}
















// function setModal(triggerSelector, modalContent, modalId) {
//   // Check if the modal already exists, and remove it if it does
//   if ($('#' + modalId).length) {
//       $('#' + modalId).remove();
//   }

//   // Create the modal HTML with the provided content and a unique ID
//   const modalHtml = `
//       <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
//           <div class="modal-dialog">
//               <div class="modal-content">
//                   <div class="modal-header">
//                       <h5 class="modal-title" id="${modalId}Label">Modal Title</h5>
//                       <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
//                   </div>
//                   <div class="modal-body">
//                       ${modalContent}
//                   </div>
//                   <div class="modal-footer">
//                       <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
//                   </div>
//               </div>
//           </div>
//       </div>
//   `;

//   // Append the modal to the body
//   $('body').append(modalHtml);

//   // Use Bootstrap to handle the modal
//   const modalInstance = new bootstrap.Modal(document.getElementById(modalId), {
//       keyboard: false
//   });

//   // Attach event listener to the trigger
//   $(triggerSelector).on('click', function() {
//       console.log('Trigger clicked');
//       modalInstance.show();
//   });

//   // Dynamically attach event listeners to buttons inside the modal
//   // $('#' + modalId + ' .modal-body').find('button[id]').each(function() {
//   //     const buttonId = $(this).attr('id');
//   //     // Example: Attach a click event listener to the button
//   //     $(this).on('click', function() {
//   //         console.log(buttonId + ' was clicked');
//   //         // You can call a function here based on buttonId
//   //     });
//   // });
// }




// function setModal(triggerSelector, modalContent) {
//   // Create the modal HTML with the provided content
//   const modalHtml = `
//       <div class="modal fade" id="dynamicModal" tabindex="-1" aria-labelledby="dynamicModalLabel" aria-hidden="true">
//           <div class="modal-dialog">
//               <div class="modal-content">
//                   <div class="modal-header">
//                       <h5 class="modal-title" id="dynamicModalLabel">Modal Title</h5>
//                       <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
//                   </div>
//                   <div class="modal-body">
//                       ${modalContent}
//                   </div>
//                   <div class="modal-footer">
//                       <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
//                   </div>
//               </div>
//           </div>
//       </div>
//   `;

//   // Append the modal to the body
//   $('body').append(modalHtml);

//   // Use the Bootstrap modal JavaScript to handle the modal
//   const modalInstance = new bootstrap.Modal(document.getElementById('dynamicModal'), {
//       keyboard: false
//   });

//   // Attach event listener to the trigger
//   $(triggerSelector).on('click', function() {
//       modalInstance.show();
//   });
// }
















// function showModal(id, title, message, onConfirm) {
//   // Find modal elements
//   const modal = document.getElementById(id);
//   const modalTitle = modal.querySelector('.modal-title');
//   const modalBody = modal.querySelector('.modal-body');
//   const confirmBtn = modal.querySelector('#confirmAction');

//   // Update the modal title and body
//   modalTitle.textContent = title;
//   modalBody.innerHTML = message; // Using innerHTML to support HTML content like links

//   // Show the modal
//   const bootstrapModal = new bootstrap.Modal(modal);
//   bootstrapModal.show();

//   if (onConfirm) {
//       // If an onConfirm function is provided, set up the confirm button
//       confirmBtn.style.display = 'inline-block'; // Make sure the button is visible
//       const handleConfirmClick = () => {
//           if (typeof onConfirm === 'function') {
//               onConfirm();
//           }
//           bootstrapModal.hide();
//       };

//       // Ensure we don't stack event listeners
//       confirmBtn.removeEventListener('click', handleConfirmClick);
//       confirmBtn.addEventListener('click', handleConfirmClick);
//   } else {
//       // If no onConfirm is provided, hide the confirm button if it exists
//       if (confirmBtn) confirmBtn.style.display = 'none';
//   }
// }






function confirmCash() {
  try {
    const body = $('body'); // Use Cash to select the document body
    if (body.length > 0) { // Successfully selected the body
      console.log('Cash was imported successfully and works.');
    } else {
      console.log('Cash could not access the DOM.');
    }
  } catch (error) {
    console.log('Error confirming Cash:', error);
  }
}



async function confirmAxios() {
  try {
    const response = await axios.get('https://jsonplaceholder.typicode.com/posts/1');
    if (response.status === 200) {
      console.log('Axios was imported successfully and works.');
    } else {
      console.log('Axios did not work as expected.');
    }
  } catch (error) {
    console.log('Error confirming Axios:', error);
  }
}





function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}



const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"][data-bs-html="true"]'))
tooltipTriggerList.forEach(function (tooltipTriggerEl) {
  new bootstrap.Tooltip(tooltipTriggerEl, {
    html: true  // Enables HTML content inside tooltips
  });
});

