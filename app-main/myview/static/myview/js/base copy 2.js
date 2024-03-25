// Confirm that cash are loaded
console.log(`base.js: ${confirmCash()}`);

// Confirm that axios are loaded
confirmAxios().then(response => {
  console.log(response);
}).catch(error => {
  console.error(error);
});

// confirm that qs are loaded
console.log(`qs: ${Qs}`);




/**
 * Perform a REST AJAX request.
 * @param {string} method - The HTTP method ('GET', 'POST', 'DELETE', etc.)
 * @param {string} url - The URL endpoint.
 * @param {Object|FormData} data - The data to be sent. Pass an object for JSON, FormData for form data.
 * @param {Object} headers - Optional. Additional headers to send.
 */
async function restAjax(method, url, data = {}, headers = {}) {
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
      const response = await axios({
          method: method,
          url: url,
          data: isFormData ? data : Qs.stringify(data),
          headers: headers,
          withCredentials: true,
      });

      // Handle response
      console.log('Response:', response.data);
      return response.data;
  } catch (error) {
      console.error('AJAX request failed:', error);
      throw error; // Re-throw to let the caller handle it
  }
}





// async function sendAuthenticatedAjax(url, action, data) {
//   try {
//       // Get CSRF token from the cookie
//       const csrfToken = getCookie('csrftoken');

//       // Prepare data with the action
//       const formData = { action, ...data };

//       // Global axios defaults
//       axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
//       axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
//       axios.defaults.headers.post['X-CSRFToken'] = csrfToken;

//       // Use axios to send a post request
//       const response = await axios.post(url, Qs.stringify(formData), {withCredentials: true});

//       console.log(response.data);
//       return response.data;
//   } catch (error) {
//       console.error('Error making AJAX call:', error);
//       return { error: 'Failed to make AJAX call' };
//   }
// }


// async function sendAuthenticatedAjax(url, data) {
//     try {
//       // Get CSRF token from the cookie
//       const csrfToken = getCookie('csrftoken');
  
//       // Make sure data is form-urlencoded or adjust the headers/content-type accordingly
//       const formData = new URLSearchParams();
//       for (const key in data) {
//         formData.append(key, data[key]);
//       }
  
//       printCurlCommand(url, csrfToken, formData);

//       // Send the request
//       const response = await fetch(url, {
//         method: 'POST', // Or 'GET', depending on your needs
//         headers: {
//           'Content-Type': 'application/x-www-form-urlencoded',
//           'X-CSRFToken': csrfToken,
//         },
//         body: formData,
//         credentials: 'include', // Ensures cookies, like session id, are sent with the request
//       });

    
//       // Check if the response is ok (status in the range 200-299)
//       if (!response.ok) {
//         throw new Error(`HTTP error! status: ${response.status}`);
//       }
  
//       // Parse the JSON response
//       const jsonResponse = await response.json();
//       return jsonResponse;
//     } catch (error) {
//       console.error('Error making AJAX call:', error);
//       return { error: 'Failed to make AJAX call' };
//     }
// }




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



















function showModal(id, title, message, onConfirm) {
  // Find modal elements
  const modal = document.getElementById(id);
  const modalTitle = modal.querySelector('.modal-title');
  const modalBody = modal.querySelector('.modal-body');
  const confirmBtn = modal.querySelector('#confirmAction');

  // Update the modal title and body
  modalTitle.textContent = title;
  modalBody.innerHTML = message; // Using innerHTML to support HTML content like links

  // Show the modal
  const bootstrapModal = new bootstrap.Modal(modal);
  bootstrapModal.show();

  if (onConfirm) {
      // If an onConfirm function is provided, set up the confirm button
      confirmBtn.style.display = 'inline-block'; // Make sure the button is visible
      const handleConfirmClick = () => {
          if (typeof onConfirm === 'function') {
              onConfirm();
          }
          bootstrapModal.hide();
      };

      // Ensure we don't stack event listeners
      confirmBtn.removeEventListener('click', handleConfirmClick);
      confirmBtn.addEventListener('click', handleConfirmClick);
  } else {
      // If no onConfirm is provided, hide the confirm button if it exists
      if (confirmBtn) confirmBtn.style.display = 'none';
  }
}





// function on(selector, eventType, handler) {
//   document.querySelectorAll(selector).forEach((element) => {
//       element.addEventListener(eventType, handler);
//   });
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
    