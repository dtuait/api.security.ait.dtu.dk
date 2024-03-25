console.log('base.js');

async function sendAuthenticatedAjax(url, data) {
    try {
      // Get CSRF token from the cookie
      const csrfToken = getCookie('csrftoken');
  
      // Make sure data is form-urlencoded or adjust the headers/content-type accordingly
      const formData = new URLSearchParams();
      for (const key in data) {
        formData.append(key, data[key]);
      }
  
      printCurlCommand(url, csrfToken, formData);

      // Send the request
      const response = await fetch(url, {
        method: 'POST', // Or 'GET', depending on your needs
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken,
        },
        body: formData,
        credentials: 'include', // Ensures cookies, like session id, are sent with the request
      });

    
      // Check if the response is ok (status in the range 200-299)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      // Parse the JSON response
      const jsonResponse = await response.json();
      return jsonResponse;
    } catch (error) {
      console.error('Error making AJAX call:', error);
      return { error: 'Failed to make AJAX call' };
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





function on(selector, eventType, handler) {
  document.querySelectorAll(selector).forEach((element) => {
      element.addEventListener(eventType, handler);
  });
}