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
 * @returns {Promise<Object>} The response data or an error object.
 */
async function restAjax(method, url, data = {}, headers = {}) {
  
  let response;
  try {
      // Determine if the data is FormData or JSON, and adjust headers accordingly
      const isFormData = data instanceof FormData;
      if (!isFormData && !(data instanceof URLSearchParams) && data !== null && Object.keys(data).length !== 0) {
          data = JSON.stringify(data); // Convert data to JSON string if it's an object
          headers['Content-Type'] = 'application/json'; // Set appropriate content type for JSON
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

    return response;

  } catch (error) {
    console.error('AJAX request failed:', error);
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
 * @param {Object} options - Optional settings for modal customization including sub modals.
 */
function setModal(triggerSelector, modalId, options = {}) {
  if ($('#' + modalId).length) {
    $('#' + modalId).remove(); // Ensure no duplicate modals
  }

  // Decompose options with defaults
  const {modalType = 'modal-dialog', modalContent = 'modal-content', title = 'Default Modal Title',
         body = 'Default Modal Body', footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`,
         eventListeners = []} = options;

  const modalHtml = createModalHtml(modalId, modalType, modalContent, title, body, footer);
  $('body').append(modalHtml);

  const modalInstance = new bootstrap.Modal(document.getElementById(modalId), { keyboard: false });

  attachEventListeners(modalId, eventListeners);

  if (triggerSelector) {
    $(triggerSelector).off('click').on('click', function () {
      modalInstance.show();
    });
  }
}

function createModalHtml(modalId, modalType, modalContent, title, body, footer) {
  return `
    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
        <div class="${modalType}">
            <div class="${modalContent}">
                <div class="modal-header">
                    <h5 class="modal-title" id="${modalId}Label">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    ${body}
                </div>
                <div class="modal-footer">
                    ${footer}
                </div>
            </div>
        </div>
    </div>
  `;
}

function attachEventListeners(modalId, eventListeners) {
  eventListeners.forEach(({selector, event, handler, subModalOptions}) => {
    // Optional subModal support
    if (subModalOptions) {
      const modifiedHandler = function() {
        handler.apply(this, arguments); // Execute original handler
        // Create subModal
        setModal(null, subModalOptions.id, subModalOptions);
      };
      $(document).off(event, `#${modalId} ${selector}`).on(event, `#${modalId} ${selector}`, modifiedHandler);
    } else {
      $(document).off(event, `#${modalId} ${selector}`).on(event, `#${modalId} ${selector}`, handler);
    }
  });
}



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


// enables tips like this <i class="bi bi-question-circle-fill" data-bs-toggle="tooltip" data-bs-placement="right" title="Tooltip on right"></i>
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"][data-bs-html="true"]'))
tooltipTriggerList.forEach(function (tooltipTriggerEl) {
  new bootstrap.Tooltip(tooltipTriggerEl, {
    html: true  // Enables HTML content inside tooltips
  });
});






















/**
//  * Dynamically creates and attaches a modal to a trigger element.
//  * 
//  * @param {string} triggerSelector - Selector for the element that triggers the modal.
//  * @param {string} modalId - Unique ID for the modal.
//  * @param {Object} options - Optional settings for modal customization.
//  */
// function setModal(triggerSelector, modalId, options = {}) {
//   // this function assumes that each that a mudal is uniqie to a trigger

  
//   if ($('#' + modalId).length) {
//     $('#' + modalId).remove();
//   }

//   // if options are provided, use them to update the modal

//   const modalType = options.modalType || 'modal-dialog'
//   const modalContent = options.modalContent || 'modal-content';
//   const modalTitle = options.title || 'Default Modal Title';
//   const modalBody = options.body || 'Default Modal Body';
//   const modalFooter = options.footer || `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`;
//   const eventListeners = options.eventListeners || []; // This will be an array of event listener descriptions

//   // Create the modal HTML with the provided content and a unique ID
//   const modalHtml = `
//       <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
//           <div class="${modalType}">
//               <div class="${modalContent}">
//                   <div class="modal-header">
//                       <h5 class="modal-title" id="${modalId}Label">${modalTitle}</h5>
//                       <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
//                   </div>
//                   <div class="modal-body">
//                       ${modalBody}
//                   </div>
//                   <div class="modal-footer">
//                       ${modalFooter}
//                   </div>
//               </div>
//           </div>
//       </div>
//   `;

//   // Append the modal to the body
//   $('body').append(modalHtml);
//   const modalInstance = new bootstrap.Modal(document.getElementById(modalId), { keyboard: false });
//   // // Use Bootstrap to handle the modal
//   // const modalInstance = new bootstrap.Modal(document.getElementById(modalId), {
//   //   keyboard: false
//   // });

//   // Attach event listeners specified in options
//   eventListeners.forEach(({selector, event, handler}) => {
//     // remove existing event listeners to prevent multiple bindings
//     $(document).off(event, `#${modalId} ${selector}`).on(event, `#${modalId} ${selector}`, handler);
//     // $(document).on(event, `#${modalId} ${selector}`, handler);
//   });

//   // Detach existing click events to prevent multiple bindings
//   $(triggerSelector).off('click').on('click', function () {
//     console.log('Trigger clicked');
//     modalInstance.show();
//   });

// }