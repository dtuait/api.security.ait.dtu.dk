// base-classes.js

export class BaseUIBinder {
    constructor() {
      if (!BaseUIBinder.instance) {
        this.baseNotificationsContainer = document.getElementById('base-notifications-container');
        BaseUIBinder.instance = this;
      }
      return BaseUIBinder.instance;
    }
  
    displayNotification(message, type, timeout = 0) {
      // Clear any existing notifications
      this.baseNotificationsContainer.innerHTML = '';
  
      const notificationDiv = document.createElement('div');
      notificationDiv.className = `alert ${type} alert-dismissible fade show`;
      notificationDiv.setAttribute('role', 'alert');
      notificationDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
  
      this.baseNotificationsContainer.appendChild(notificationDiv);
  
      if (timeout > 0) {
        setTimeout(() => {
          this.baseNotificationsContainer.innerHTML = '';
        }, timeout);
      }
  
      return true;
    }
  
  
      /**
     * Dynamically creates and attaches a modal to a trigger element.
     * @param {string} triggerSelector - Selector for the element that triggers the modal.
     * @param {string} modalId - Unique ID for the modal.
     * @param {Object} options - Optional settings for modal customization.
     */
    setModal(triggerSelector, modalId, options = {}) {
      // Remove existing modal if it exists
      const existingModal = document.getElementById(modalId);
      if (existingModal) {
        existingModal.parentNode.removeChild(existingModal);
      }
  
      // Options for modal content
      const modalType = options.modalType || 'modal-dialog';
      const modalContent = options.modalContent || 'modal-content';
      const modalTitle = options.title || 'Default Modal Title';
      const modalBody = options.body || 'Default Modal Body';
      const modalFooter = options.footer || `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`;
      const eventListeners = options.eventListeners || [];
  
      // Create modal element
      const modalElement = document.createElement('div');
      modalElement.className = 'modal fade';
      modalElement.id = modalId;
      modalElement.tabIndex = -1;
      modalElement.setAttribute('aria-labelledby', `${modalId}Label`);
      modalElement.setAttribute('aria-hidden', 'true');
  
      modalElement.innerHTML = `
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
      `;
  
      // Append the modal to the body
      document.body.appendChild(modalElement);
  
      // Initialize the modal using Bootstrap's JavaScript API
      const modalInstance = new bootstrap.Modal(modalElement, { keyboard: false });
  
      // Attach event listeners specified in options
      eventListeners.forEach(({ selector, event, handler }) => {
        const elements = modalElement.querySelectorAll(selector);
        elements.forEach((element) => {
          element.addEventListener(event, handler);
        });
      });
  
      // Attach click event to the trigger to show the modal
      const triggerElement = document.querySelector(triggerSelector);
      if (triggerElement) {
        triggerElement.addEventListener('click', (e) => {
          e.preventDefault();
          modalInstance.show();
        });
      }
  
      return modalInstance;
    }
  
    /**
     * Updates the content of an existing modal.
     * @param {string} modalId - ID of the modal to update.
     * @param {Object} content - Object containing new content and event listeners.
     */
    updateModalContent(modalId, content = { modalTitle: '', modalBody: '', modalFooter: '', eventListeners: [] }) {
      // Get the modal element
      const modalElement = document.getElementById(modalId);
      if (!modalElement) {
        console.error(`Modal with ID ${modalId} not found.`);
        return;
      }
  
      // Update the modal title if provided
      if (content.modalTitle) {
        const modalTitleElement = modalElement.querySelector('.modal-title');
        if (modalTitleElement) {
          modalTitleElement.textContent = content.modalTitle;
        }
      }
  
      // Update the modal body if provided
      if (content.modalBody) {
        const modalBodyElement = modalElement.querySelector('.modal-body');
        if (modalBodyElement) {
          modalBodyElement.innerHTML = content.modalBody;
        }
      }
  
      // Update the modal footer if provided
      if (content.modalFooter) {
        const modalFooterElement = modalElement.querySelector('.modal-footer');
        if (modalFooterElement) {
          modalFooterElement.innerHTML = content.modalFooter;
        }
      }
  
      // Attach event listeners specified in options
      const eventListeners = content.eventListeners || [];
      eventListeners.forEach(({ selector, event, handler }) => {
        const elements = modalElement.querySelectorAll(selector);
        elements.forEach((element) => {
          // Remove existing event listeners to prevent multiple bindings
          const newElement = element.cloneNode(true);
          element.parentNode.replaceChild(newElement, element);
          newElement.addEventListener(event, handler);
        });
      });
    }
  
    static getInstance() {
      if (!BaseUIBinder.instance) {
        BaseUIBinder.instance = new BaseUIBinder();
      }
      return BaseUIBinder.instance;
    }
  }
  
  export class BaseAppUtils {
    constructor() {
      if (!BaseAppUtils.instance) {
        BaseAppUtils.instance = this;
      }
      return BaseAppUtils.instance;
    }
  
    async restAjax(method, url, data = null, headers = {}) {
      // Add CSRF token for Django compatibility
      const csrfToken = this.getCookie('csrftoken');
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
  
      let body = null;
  
      if (data) {
        if (data instanceof FormData) {
          body = data;
        } else if (typeof data === 'object') {
          headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';
          body = new URLSearchParams(data).toString();
        } else if (typeof data === 'string') {
          headers['Content-Type'] = 'application/json';
          body = data;
        } else {
          throw new Error('Invalid data type: data must be an Object, FormData, or JSON string');
        }
      }
  
      try {
        const response = await fetch(url, {
          method: method,
          headers: headers,
          body: (method !== 'GET' && method !== 'HEAD') ? body : undefined,
          credentials: 'include',
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
  
        if (response.status === 204) {
          return {};
        } else {
          return await response.json();
        }
      } catch (error) {
        console.error('Request failed:', error);
        throw error;
      }
    }
  
    getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
      return null;
    }
  
    updateSessionStorage(data, prefix) {
      for (let key in data) {
        if (data.hasOwnProperty(key)) {
          let jsonData = JSON.stringify(data[key]);
          sessionStorage.setItem(`${prefix}-${key}`, jsonData);
        }
      }
    }
  
      /**
     * Dynamically creates and attaches a modal to a trigger element.
     * @param {string} triggerSelector - Selector for the element that triggers the modal.
     * @param {string} modalId - Unique ID for the modal.
     * @param {Object} options - Optional settings for modal customization.
     */
      setModal(triggerSelector, modalId, options = {}) {
        // Remove existing modal if it exists
        const existingModal = document.getElementById(modalId);
        if (existingModal) {
          existingModal.parentNode.removeChild(existingModal);
        }
    
        // Options for modal content
        const modalType = options.modalType || 'modal-dialog';
        const modalContent = options.modalContent || 'modal-content';
        const modalTitle = options.title || 'Default Modal Title';
        const modalBody = options.body || 'Default Modal Body';
        const modalFooter = options.footer || `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`;
        const eventListeners = options.eventListeners || [];
    
        // Create modal element
        const modalElement = document.createElement('div');
        modalElement.className = 'modal fade';
        modalElement.id = modalId;
        modalElement.tabIndex = -1;
        modalElement.setAttribute('aria-labelledby', `${modalId}Label`);
        modalElement.setAttribute('aria-hidden', 'true');
    
        modalElement.innerHTML = `
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
        `;
    
        // Append the modal to the body
        document.body.appendChild(modalElement);
    
        // Initialize the modal using Bootstrap's JavaScript API
        const modalInstance = new bootstrap.Modal(modalElement, { keyboard: false });
    
        // Attach event listeners specified in options
        eventListeners.forEach(({ selector, event, handler }) => {
          const elements = modalElement.querySelectorAll(selector);
          elements.forEach((element) => {
            element.addEventListener(event, handler);
          });
        });
    
        // Attach click event to the trigger to show the modal
        const triggerElement = document.querySelector(triggerSelector);
        if (triggerElement) {
          triggerElement.addEventListener('click', (e) => {
            e.preventDefault();
            modalInstance.show();
          });
        }
    
        return modalInstance;
      }
    
      /**
       * Updates the content of an existing modal.
       * @param {string} modalId - ID of the modal to update.
       * @param {Object} content - Object containing new content and event listeners.
       */
      updateModalContent(modalId, content = { modalTitle: '', modalBody: '', modalFooter: '', eventListeners: [] }) {
        // Get the modal element
        const modalElement = document.getElementById(modalId);
        if (!modalElement) {
          console.error(`Modal with ID ${modalId} not found.`);
          return;
        }
    
        // Update the modal title if provided
        if (content.modalTitle) {
          const modalTitleElement = modalElement.querySelector('.modal-title');
          if (modalTitleElement) {
            modalTitleElement.textContent = content.modalTitle;
          }
        }
    
        // Update the modal body if provided
        if (content.modalBody) {
          const modalBodyElement = modalElement.querySelector('.modal-body');
          if (modalBodyElement) {
            modalBodyElement.innerHTML = content.modalBody;
          }
        }
    
        // Update the modal footer if provided
        if (content.modalFooter) {
          const modalFooterElement = modalElement.querySelector('.modal-footer');
          if (modalFooterElement) {
            modalFooterElement.innerHTML = content.modalFooter;
          }
        }
    
        // Attach event listeners specified in options
        const eventListeners = content.eventListeners || [];
        eventListeners.forEach(({ selector, event, handler }) => {
          const elements = modalElement.querySelectorAll(selector);
          elements.forEach((element) => {
            // Remove existing event listeners to prevent multiple bindings
            const newElement = element.cloneNode(true);
            element.parentNode.replaceChild(newElement, element);
            newElement.addEventListener(event, handler);
          });
        });
      }
  
    static initializeTooltips() {
      try {
        const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"][data-bs-html="true"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
          new bootstrap.Tooltip(tooltipTriggerEl, {
            html: true,
          });
        });
      } catch (error) {
        console.error('Failed to load tooltips styling:', error);
        throw new Error('Failed to load tooltips styling');
      }
    }
  
    static getInstance() {
      if (!BaseAppUtils.instance) {
        BaseAppUtils.instance = new BaseAppUtils();
      }
      return BaseAppUtils.instance;
    }
  }
  