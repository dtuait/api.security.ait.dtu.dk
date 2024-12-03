import { BaseUIBinder, BaseAppUtils } from "./base-classes.js";

console.log('Active Directory Copilot JS loaded');

class App {
    constructor(uiBinder = UIBinder.getInstance(), baseAppUtils = BaseAppUtils.getInstance()) {
        if (!App.instance) {
            this.uiBinder = uiBinder;
            this.baseAppUtils = baseAppUtils;
            this.currentThreadId = null;
            this._setBindings();
            this.init();
            App.instance = this;
        }
        return App.instance;
    }

    init() {
        this.loadChatThreads();
    }

    _setBindings() {
        // Send button click
        this.uiBinder.sendBtn.addEventListener('click', (event) => {
            event.preventDefault();
            this.handleUserInput();
        });

        // Enter key in textarea
        this.uiBinder.userInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                this.handleUserInput();
            }
        });

        // New Chat button
        this.uiBinder.newChatBtn.addEventListener('click', (event) => {
            event.preventDefault();
            this.createNewChat();
        });

        // Chat thread click
        this.uiBinder.chatList.addEventListener('click', (event) => {
            const threadItem = event.target.closest('.chat-thread-item');
            if (threadItem && !event.target.classList.contains('delete-chat-btn') && !event.target.classList.contains('edit-chat-btn')) {
                const threadId = threadItem.dataset.threadId;
                this.loadChatMessages(threadId);
            }

            // Delete chat thread
            const deleteBtn = event.target.closest('.delete-chat-btn');
            if (deleteBtn) {
                const threadId = deleteBtn.dataset.threadId;
                const threadTitle = deleteBtn.parentElement.querySelector('.thread-title').textContent;
                this.confirmDeleteChatThread(threadId, threadTitle);
            }

            // Edit chat thread title
            const editBtn = event.target.closest('.edit-chat-btn');
            if (editBtn) {
                const threadId = editBtn.dataset.threadId;
                this.uiBinder.enableTitleEditing(threadId);
            }
        });

        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('run-query-btn')) {
                const messageElement = event.target.closest('.assistant-message');
                const queryParameters = this.uiBinder.getQueryParameters(messageElement);
                this.runQuery(queryParameters, messageElement);
            }

            if (event.target.classList.contains('download-excel-btn')) {
                const messageElement = event.target.closest('.assistant-message');
                const queryParameters = this.uiBinder.getQueryParameters(messageElement);
                this.downloadExcel(queryParameters, messageElement);
            }
        });

        // Handle browser navigation (back/forward)
        window.addEventListener('popstate', (event) => {
            const threadId = event.state ? event.state.threadId : null;
            if (threadId) {
                this.loadChatMessages(threadId, false); // Don't push state again
            } else {
                // If no threadId in history state, load default or clear messages
                this.currentThreadId = null;
                this.uiBinder.clearChatMessages();
            }
        });
    }

    async updateThreadTitle(threadId, newTitle) {
        try {
            await this.baseAppUtils.restAjax('POST', '/myview/ajax/', {
                'action': 'update_chat_thread_title',
                'thread_id': threadId,
                'title': newTitle
            });
            // Optionally, refresh the chat threads list
            this.loadChatThreads();
        } catch (error) {
            console.error('Error updating thread title:', error);
            throw error;
        }
    }

    async createNewChat() {
        try {
            const response = await this.baseAppUtils.restAjax('POST', '/myview/ajax/', {
                'action': 'create_chat_thread'
            });
            this.currentThreadId = response.thread_id;
            if (response.existing) {
                // Load existing messages
                await this.loadChatMessages(this.currentThreadId);
            } else {
                // Clear messages for new chat
                this.uiBinder.clearChatMessages();
            }
            this.loadChatThreads();
        } catch (error) {
            console.error('Error creating new chat:', error);
        }
    }

    async loadChatThreads() {
        try {
            const response = await this.baseAppUtils.restAjax('POST', '/myview/ajax/', {
                'action': 'get_chat_threads'
            });
            this.uiBinder.populateChatThreads(response.threads);

            if (response.threads.length > 0) {
                let threadId = this.getThreadIdFromURL();

                // Validate if the threadId exists in the threads list
                if (threadId && response.threads.some(thread => thread.id == threadId)) {
                    this.currentThreadId = threadId;
                } else {
                    // Default to the first thread if threadId is invalid
                    this.currentThreadId = response.threads[0].id;
                    // Update the URL to reflect the default thread
                    this.updateURL(this.currentThreadId);
                }
                this.loadChatMessages(this.currentThreadId, false); // Pass false to avoid pushing state again
            }
        } catch (error) {
            console.error('Error loading chat threads:', error);
        }
    }

    async loadChatMessages(threadId, pushState = true) {
        this.currentThreadId = threadId;

        // Update the URL without reloading the page
        if (pushState) {
            this.updateURL(threadId);
        }

        try {
            const response = await this.baseAppUtils.restAjax('POST', '/myview/ajax/', {
                'action': 'get_chat_messages',
                'thread_id': threadId
            });
            this.uiBinder.clearChatMessages();
            response.messages.forEach(message => {
                if (message.role === 'user') {
                    this.uiBinder.appendUserMessage(message.content, message.timestamp);
                } else if (message.role === 'assistant') {
                    this.uiBinder.appendAssistantMessage(JSON.parse(message.content), message.timestamp);
                }
            });
        } catch (error) {
            console.error('Error loading chat messages:', error);
        }

        this.uiBinder.bindTextareaAutoResize(this.uiBinder.messagesContainer);
    }

    // Updated method to update the URL with query parameter
    updateURL(threadId) {
        const url = new URL(window.location);
        url.searchParams.set('threadId', threadId);
        window.history.pushState({ threadId: threadId }, '', url);
    }

    // Updated method to extract threadId from query parameter
    getThreadIdFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const threadId = urlParams.get('threadId');
        return threadId;
    }

    async handleUserInput() {
        const userInput = this.uiBinder.userInput.value.trim();
        if (userInput === '') {
            return;
        }

        if (!this.currentThreadId) {
            await this.createNewChat();
        }

        // Append user's message to chat
        this.uiBinder.appendUserMessage(userInput);

        // Clear input
        this.uiBinder.userInput.value = '';

        // Show loading indicator
        this.uiBinder.showLoading();

        try {
            const response = await this.baseAppUtils.restAjax('POST', '/myview/ajax/', {
                'action': 'send_message',
                'thread_id': this.currentThreadId,
                'message': userInput
            });

            // Hide loading indicator
            this.uiBinder.hideLoading();

            // Display assistant's response
            const assistantResponse = response.assistant_response;
            const assistantMessageElement = this.uiBinder.appendAssistantMessage(assistantResponse);

            // Reload chat threads to update titles
            this.loadChatThreads();

            // Check if auto-run is enabled
            if (this.uiBinder.autoRunToggle.checked) {
                // Simulate clicking the "Run Query" button
                const runQueryBtn = assistantMessageElement.querySelector('.run-query-btn');
                if (runQueryBtn) {
                    runQueryBtn.click();
                }
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.uiBinder.hideLoading();
            this.uiBinder.appendAssistantMessage({ error: error.message });
        }
    }

    // Updated runQuery method
    async runQuery(queryParameters, messageElement) {
        try {
            // Collect the current values from the editable fields
            const baseDnInput = messageElement.querySelector('textarea[name="base_dn"]');
            const searchFilterInput = messageElement.querySelector('textarea[name="search_filter"]');
            const searchAttributesInput = messageElement.querySelector('textarea[name="search_attributes"]');
            const limitInput = messageElement.querySelector('textarea[name="limit"]');
            const excludedAttributesInput = messageElement.querySelector('textarea[name="excluded_attributes"]');

            const base_dn = baseDnInput ? baseDnInput.value : queryParameters.base_dn;
            const search_filter = searchFilterInput ? searchFilterInput.value : queryParameters.search_filter;
            const search_attributes = searchAttributesInput ? searchAttributesInput.value : queryParameters.search_attributes;
            const limit = limitInput ? limitInput.value : queryParameters.limit;
            const excluded_attributes = excludedAttributesInput ? excludedAttributesInput.value : queryParameters.excluded_attributes;

            // Prepare form data
            const formData = new FormData();
            formData.append('action', 'active_directory_query');
            formData.append('base_dn', base_dn);
            formData.append('search_filter', search_filter);
            formData.append('search_attributes', search_attributes);
            formData.append('limit', limit);
            formData.append('excluded_attributes', excluded_attributes);
            formData.append('csrfmiddlewaretoken', this.getCookie('csrftoken'));

            // Run the query via the AJAX endpoint
            const response = await fetch('/myview/ajax/', {
                method: 'POST',
                body: formData,
                credentials: 'same-origin' // Include cookies for authentication
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();

            // Display the result
            this.uiBinder.appendQueryResultMessage(result, messageElement);

        } catch (error) {
            console.error('Error running query:', error);
            // Display error message
            this.uiBinder.appendQueryResultMessage({ error: error.message }, messageElement);
        }
    }

    async downloadExcel(queryParameters, messageElement) {
        try {
            // Collect the current values from the editable fields
            const baseDnInput = messageElement.querySelector('textarea[name="base_dn"]');
            const searchFilterInput = messageElement.querySelector('textarea[name="search_filter"]');
            const searchAttributesInput = messageElement.querySelector('textarea[name="search_attributes"]');
            const limitInput = messageElement.querySelector('textarea[name="limit"]');
            const excludedAttributesInput = messageElement.querySelector('textarea[name="excluded_attributes"]');

            const base_dn = baseDnInput ? baseDnInput.value : queryParameters.base_dn;
            const search_filter = searchFilterInput ? searchFilterInput.value : queryParameters.search_filter;
            const search_attributes = searchAttributesInput ? searchAttributesInput.value : queryParameters.search_attributes;
            const limit = limitInput ? limitInput.value : queryParameters.limit;
            const excluded_attributes = excludedAttributesInput ? excludedAttributesInput.value : queryParameters.excluded_attributes;

            // Prepare form data
            const formData = new FormData();
            formData.append('action', 'generate_excel');
            formData.append('base_dn', base_dn);
            formData.append('search_filter', search_filter);
            formData.append('search_attributes', search_attributes);
            formData.append('limit', limit);
            formData.append('excluded_attributes', excluded_attributes);
            formData.append('csrfmiddlewaretoken', this.getCookie('csrftoken'));

            // Make a POST request to ajax_view.py
            const response = await fetch('/myview/ajax/', {
                method: 'POST',
                body: formData,
                credentials: 'same-origin' // Include cookies for authentication
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();

            if (result.download_url) {
                // Use window.location.origin to get the base URL
                const downloadUrl = window.location.origin + result.download_url;

                // Now use downloadUrl when creating the link
                // Create a temporary link to download the file
                const link = document.createElement('a');
                link.href = downloadUrl; // Use the absolute URL here
                link.download = 'active_directory_query.xlsx';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                throw new Error('Failed to generate Excel file.');
            }

        } catch (error) {
            console.error('Error generating Excel file:', error);
            alert('Error generating Excel file: ' + error.message);
        }
    }

    // Helper function to get CSRF token
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    confirmDeleteChatThread(threadId, threadTitle) {
        const modalId = 'deleteChatModal';

        // Use BaseAppUtils setModal to create the modal
        this.baseAppUtils.setModal(null, modalId, {
            title: 'Delete Chat',
            body: `<p>Are you sure you want to delete "<strong>${this.uiBinder.escapeHtml(threadTitle)}</strong>"?</p>`,
            footer: `
                <button type="button" class="btn btn-danger" id="confirmDeleteBtn">Delete</button>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            `,
            eventListeners: [
                {
                    selector: '#confirmDeleteBtn',
                    event: 'click',
                    handler: (event) => {
                        this.deleteChatThread(threadId, modalId);
                    }
                }
            ]
        });

        // Show the modal
        const modalInstance = new bootstrap.Modal(document.getElementById(modalId));
        modalInstance.show();
    }

    async deleteChatThread(threadId, modalId) {
        try {
            await this.baseAppUtils.restAjax('POST', '/myview/ajax/', {
                'action': 'delete_chat_thread',
                'thread_id': threadId
            });

            // Close the modal
            const modalElement = document.getElementById(modalId);
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            modalInstance.hide();

            // Refresh chat threads
            await this.loadChatThreads();

            // If the deleted thread was the current one, clear the messages
            if (this.currentThreadId === threadId) {
                this.currentThreadId = null;
                this.uiBinder.clearChatMessages();
            }

        } catch (error) {
            console.error('Error deleting chat thread:', error);
        }
    }

    static getInstance(uiBinder = UIBinder.getInstance(), baseAppUtils = BaseAppUtils.getInstance()) {
        if (!App.instance) {
            App.instance = new App(uiBinder, baseAppUtils);
        }
        return App.instance;
    }
}

class UIBinder {
    constructor() {
        if (!UIBinder.instance) {
            this.sendBtn = document.getElementById('send-btn');
            this.userInput = document.getElementById('user-input');
            this.chatMessages = document.getElementById('chat-messages');
            this.messagesContainer = document.getElementById('messages-container');
            this.chatDetail = document.getElementById('chat-detail');
            this.splitter = document.getElementById('splitter');
            this.toggleChatDetailBtn = document.getElementById('toggle-chat-detail');
            this.chatList = document.getElementById('chat-list');
            this.newChatBtn = document.getElementById('new-chat-btn');
            this.loadingIndicator = this.createLoadingIndicator();
            this.autoRunToggle = document.getElementById('auto-run-toggle');
            this.userSettings = this.loadUserSettings();

            // Initialize the splitter functionality
            this.initSplitter();
            this.initializeToggles();

            // Bind the collapse button
            this.toggleChatDetailBtn.addEventListener('click', () => {
                this.toggleChatDetail();
            });

            UIBinder.instance = this;
        }
        return UIBinder.instance;
    }

    loadUserSettings() {
        const settings = localStorage.getItem('active-directory-copilot');
        if (settings) {
            return JSON.parse(settings);
        } else {
            // Default settings
            return {
                autoRunQueryEnabled: false,
                displayAsCSVEnabled: false
            };
        }
    }

    saveUserSettings() {
        localStorage.setItem('active-directory-copilot', JSON.stringify(this.userSettings));
    }

    initializeToggles() {
        // Initialize Auto Run Query toggle
        if (this.autoRunToggle) {
            this.autoRunToggle.checked = this.userSettings.autoRunQueryEnabled;
            this.autoRunToggle.addEventListener('change', () => {
                this.userSettings.autoRunQueryEnabled = this.autoRunToggle.checked;
                this.saveUserSettings();
            });
        }
    }

    getQueryParameters(messageElement) {
        const baseDnInput = messageElement.querySelector('textarea[name="base_dn"]');
        const searchFilterInput = messageElement.querySelector('textarea[name="search_filter"]');
        const searchAttributesInput = messageElement.querySelector('textarea[name="search_attributes"]');
        const limitInput = messageElement.querySelector('textarea[name="limit"]');
        const excludedAttributesInput = messageElement.querySelector('textarea[name="excluded_attributes"]');
    
        return {
            base_dn: baseDnInput ? baseDnInput.value : '',
            search_filter: searchFilterInput ? searchFilterInput.value : '',
            search_attributes: searchAttributesInput ? searchAttributesInput.value : '',
            limit: limitInput ? limitInput.value : '',
            excluded_attributes: excludedAttributesInput ? excludedAttributesInput.value : ''
        };
    }



    bindTextareaAutoResize(container) {
        container.querySelectorAll('textarea').forEach(textarea => {
            function adjustHeight() {
                textarea.style.height = '2.5em'; // Reset to one line
                textarea.style.height = textarea.scrollHeight + 'px'; // Adjust height based on content
            }
            textarea.addEventListener('input', adjustHeight);
            // Adjust the height initially
            adjustHeight();
        });
    }

    
    // bindTextareaAutoResize() {
    //     const userInput = this.userInput;

    //     function adjustTextareaHeight() {
    //         userInput.style.height = 'auto'; // Reset height
    //         userInput.style.height = userInput.scrollHeight + 'px'; // Set new height based on content
    //     }

    //     userInput.addEventListener('input', adjustTextareaHeight);

    //     // Optionally, adjust height on initialization
    //     adjustTextareaHeight();
    // }


   

    disableTitleEditing(threadId, title) {
        const threadItem = this.chatList.querySelector(`.chat-thread-item[data-thread-id="${threadId}"]`);
        if (!threadItem) return;

        const input = threadItem.querySelector('.edit-thread-title-input');
        if (!input) return;

        const threadTitle = document.createElement('span');
        threadTitle.classList.add('thread-title');
        threadTitle.textContent = title;

        threadItem.replaceChild(threadTitle, input);
    }


    enableTitleEditing(threadId) {
        const threadItem = this.chatList.querySelector(`.chat-thread-item[data-thread-id="${threadId}"]`);
        if (!threadItem) return;

        const threadTitle = threadItem.querySelector('.thread-title');
        const currentTitle = threadTitle.textContent;

        // Create an input field
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentTitle;
        input.classList.add('edit-thread-title-input');

        // Replace the threadTitle element with the input field
        threadItem.replaceChild(input, threadTitle);

        input.focus();
        input.select();

        // Event listeners for saving the new title
        const saveTitle = () => {
            const newTitle = input.value.trim();
            if (newTitle === '') {
                // If title is empty, revert to previous title
                this.disableTitleEditing(threadId, currentTitle);
            } else {
                // Save the new title via AJAX
                App.getInstance().updateThreadTitle(threadId, newTitle)
                    .then(() => {
                        this.disableTitleEditing(threadId, newTitle);
                    })
                    .catch(error => {
                        console.error('Error updating thread title:', error);
                        this.disableTitleEditing(threadId, currentTitle);
                    });
            }
        };

        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                saveTitle();
            } else if (event.key === 'Escape') {
                this.disableTitleEditing(threadId, currentTitle);
            }
        });

        input.addEventListener('blur', () => {
            saveTitle();
        });
    }


    handleChatMessagesScroll() {
        const chatInputRect = this.chatInput.getBoundingClientRect();
        const chatWindowRect = this.chatWindow.getBoundingClientRect();

        if (chatInputRect.bottom > chatWindowRect.bottom) {
            // The chat-input is about to go off-screen upwards
            if (!this.isChatInputFixed) {
                this.chatInput.style.position = 'fixed';
                this.chatInput.style.bottom = (window.innerHeight - chatWindowRect.bottom) + 'px';
                this.chatInput.style.left = chatWindowRect.left + 'px';
                this.chatInput.style.width = chatWindowRect.width + 'px';
                this.chatInput.style.zIndex = '1000';
                this.isChatInputFixed = true;
            }
        } else {
            // Reset to normal position
            if (this.isChatInputFixed) {
                this.chatInput.style.position = '';
                this.chatInput.style.bottom = '';
                this.chatInput.style.left = '';
                this.chatInput.style.width = '';
                this.chatInput.style.zIndex = '';
                this.isChatInputFixed = false;
            }
        }
    }


    initSplitter() {
        const splitter = this.splitter;
        const chatMessages = this.chatMessages;
        const chatDetail = this.chatDetail;
        const chatContent = document.querySelector('.chat-content');

        let isDragging = false;

        splitter.addEventListener('mousedown', (e) => {
            isDragging = true;
            document.body.style.cursor = 'col-resize';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const totalWidth = chatContent.getBoundingClientRect().width;
            const offsetLeft = chatContent.getBoundingClientRect().left;
            let newX = e.clientX - offsetLeft;

            // Minimum and maximum widths
            const minChatMessagesWidth = 200; // Minimum width for chatMessages
            const minChatDetailWidth = 200;   // Minimum width for chatDetail

            // Calculate widths
            let chatMessagesWidth = newX - splitter.offsetWidth / 2;
            let chatDetailWidth = totalWidth - chatMessagesWidth - splitter.offsetWidth;

            // Enforce minimum widths
            if (chatMessagesWidth < minChatMessagesWidth) {
                chatMessagesWidth = minChatMessagesWidth;
                chatDetailWidth = totalWidth - chatMessagesWidth - splitter.offsetWidth;
            }

            if (chatDetailWidth < minChatDetailWidth) {
                chatDetailWidth = minChatDetailWidth;
                chatMessagesWidth = totalWidth - chatDetailWidth - splitter.offsetWidth;
            }

            chatMessages.style.flexBasis = `${chatMessagesWidth}px`;
            chatDetail.style.flexBasis = `${chatDetailWidth}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                document.body.style.cursor = '';
            }
        });
    }


    toggleChatDetail() {
        this.chatDetail.classList.toggle('collapsed');
        if (this.chatDetail.classList.contains('collapsed')) {
            this.chatMessages.style.flexBasis = 'calc(100% - 10px)';
            this.toggleChatDetailBtn.textContent = '<'; // Change icon
            this.splitter.style.display = 'none';
        } else {
            this.chatMessages.style.flexBasis = 'calc(60% - 5px)';
            this.toggleChatDetailBtn.textContent = '>'; // Change icon
            this.splitter.style.display = 'block';
        }
    }


    createLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-indicator';
        loadingDiv.textContent = 'Assistant is typing...';
        return loadingDiv;
    }

    appendUserMessage(message, timestamp = null) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'user-message');

        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.innerHTML = this.escapeHtml(message);

        messageElement.appendChild(messageContent);
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    ntTimeToDate(ntTimeValue) {
        const ntTime = parseInt(ntTimeValue, 10);
        const ntEpoch = new Date(Date.UTC(1601, 0, 1));
        const millisecondsSinceNtEpoch = ntTime / 10000;
        const date = new Date(ntEpoch.getTime() + millisecondsSinceNtEpoch);
        const day = date.getUTCDate().toString().padStart(2, '0');
        const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
        const year = date.getUTCFullYear();
        return `${day}-${month}-${year}`;
    }

    dateToNtTime(dateString) {
        const [day, month, year] = dateString.split('-').map(Number);
        const date = new Date(Date.UTC(year, month - 1, day));
        const ntEpoch = new Date(Date.UTC(1601, 0, 1));
        const millisecondsSinceNtEpoch = date - ntEpoch;
        const ntTime = millisecondsSinceNtEpoch * 10000;
        return ntTime.toString();
    }

    toggleResultFormat(result, resultElement, displayAsCSV) {
        const resultContent = resultElement.querySelector('.result-content');

        // Remove existing content
        resultContent.innerHTML = '';

        // Display the count
        const countElement = document.createElement('div');
        countElement.classList.add('result-count');
        countElement.textContent = `Number of objects returned: ${result.count}`;
        resultContent.appendChild(countElement);

        if (displayAsCSV) {
            // Convert JSON to CSV table and display
            const csvTable = this.convertJSONToTable(result.results);
            resultContent.appendChild(csvTable);
        } else {
            // Display JSON
            const preElement = document.createElement('pre');
            preElement.textContent = JSON.stringify(result.results, null, 2);
            resultContent.appendChild(preElement);
        }
    }

    convertJSONToTable(jsonData) {
        const table = document.createElement('table');
        table.classList.add('result-table');

        // Get all unique keys from the JSON data
        const keys = Array.from(new Set(jsonData.flatMap(item => Object.keys(item))));

        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        keys.forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create table body
        const tbody = document.createElement('tbody');
        jsonData.forEach(item => {
            const row = document.createElement('tr');
            keys.forEach(key => {
                const td = document.createElement('td');
                const value = item[key] ? item[key].join(', ') : '';
                td.textContent = value;
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        table.appendChild(tbody);

        return table;
    }

    parseSearchFilterForNtTime(searchFilter) {
        const regex = /(\(pwdLastSet<=?(\d+)\))/;
        const match = searchFilter.match(regex);
        if (match) {
            return {
                fullMatch: match[1],
                ntTimeValue: match[2]
            };
        }
        return null;
    }

    appendAssistantMessage(message, timestamp = null) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'assistant-message');
    
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
    
        // Format the message content based on the JSON data
        if (message.error) {
            messageContent.textContent = `An error occurred: ${message.error}`;
        } else {
            messageContent.innerHTML = this.formatAssistantMessageContent(message);
        }

        this.bindTextareaAutoResize(messageElement);
    
        messageElement.appendChild(messageContent);
    
        // Clear previous content and append to chat-detail
        this.chatDetail.innerHTML = '';
        this.chatDetail.appendChild(messageElement);

        // Get the baseDnInput and distinguishedNameElement elements
        const baseDnInput = messageElement.querySelector('input[name="base_dn"]');
        const distinguishedNameElement = messageElement.querySelector('#distinguished-name');

        if (baseDnInput && distinguishedNameElement) {
            baseDnInput.addEventListener('input', () => {
                const canonicalName = baseDnInput.value;
                const distinguishedName = this.canonicalToDistinguishedName(canonicalName);
                distinguishedNameElement.textContent = distinguishedName;
            });

            // Trigger the input event once to initialize
            baseDnInput.dispatchEvent(new Event('input'));
        }

        // Add event listener for baseDnInput to fetch suggestions
        if (baseDnInput) {
            baseDnInput.addEventListener('input', async () => {
                const canonicalName = baseDnInput.value;
                if (canonicalName.length < 3) return; // Wait until the user has typed at least 3 characters

                // Prepare form data
                const formData = new FormData();
                formData.append('action', 'active_directory_query');
                formData.append('base_dn', 'DC=win,DC=dtu,DC=dk');
                formData.append('search_filter', `(canonicalName=*${canonicalName}*)`);
                formData.append('search_attributes', 'canonicalName');
                formData.append('limit', '100');
                formData.append('csrfmiddlewaretoken', this.getCookie('csrftoken'));

                try {
                    const response = await fetch('/myview/ajax/', {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        // Process the result to show suggestions
                        this.showBaseDnSuggestions(baseDnInput, result.results);
                    }
                } catch (error) {
                    console.error('Error fetching base_dn suggestions:', error);
                }
            });
        }

        // Add the "Run Query" and "Download Excel" buttons
        if (!message.error) {
            const buttonContainer = document.createElement('div');
            buttonContainer.classList.add('button-container');

            const runQueryBtn = document.createElement('button');
            runQueryBtn.textContent = 'Run Query';
            runQueryBtn.classList.add('run-query-btn');
            runQueryBtn.addEventListener('click', () => {
                App.getInstance().runQuery(message, messageElement);
            });

            const downloadExcelBtn = document.createElement('button');
            downloadExcelBtn.textContent = 'Download Excel';
            downloadExcelBtn.classList.add('download-excel-btn');
            downloadExcelBtn.addEventListener('click', () => {
                App.getInstance().downloadExcel(message, messageElement);
            });

            // Append buttons to the button container
            buttonContainer.appendChild(runQueryBtn);
            buttonContainer.appendChild(downloadExcelBtn);

            messageContent.appendChild(buttonContainer);
        }

        return messageElement; // Return the element for further manipulation
    }

    // Helper function to get CSRF token
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    formatAssistantMessageContent(data) {
        let content = '';

        if (data.explanation) {
            content += `${this.escapeHtml(data.explanation)}<br><br>`;
        }

        const fields = ['base_dn', 'search_filter', 'search_attributes', 'limit', 'excluded_attributes'];
        fields.forEach(field => {
            if (data[field]) {
                if (field === 'base_dn') {
                    content += `
                    <label>
                        <strong>${this.escapeHtml(field)} (Canonical Name):</strong>
                        <input type="text" name="${field}" value="${this.escapeHtml(data[field])}" />
                    </label><br>
                    <small>Distinguished Name: <code id="distinguished-name">${this.escapeHtml(this.canonicalToDistinguishedName(data[field]))}</code></small><br>
                    `;
                } else {
                    content += `
                    <label>
                        <strong>${this.escapeHtml(field)}:</strong>
                        <input type="text" name="${field}" value="${this.escapeHtml(data[field])}" />
                    </label><br>`;
                }
            }
        });

        return content;
    }

    canonicalToDistinguishedName(canonicalName) {
        let parts = canonicalName.split('/');
        let domainParts = parts[0].split('.');
        let organizationalUnits = parts.slice(1).reverse();

        let distinguishedName = [];

        organizationalUnits.forEach(ou => {
            distinguishedName.push(`OU=${ou}`);
        });

        domainParts.forEach(dc => {
            distinguishedName.push(`DC=${dc}`);
        });

        return distinguishedName.join(',');
    }

    showBaseDnSuggestions(inputElement, suggestions) {
        let dataList = inputElement.list;
        if (!dataList) {
            dataList = document.createElement('datalist');
            dataList.id = 'baseDnSuggestions';
            document.body.appendChild(dataList);
            inputElement.setAttribute('list', 'baseDnSuggestions');
        }
        dataList.innerHTML = '';
        suggestions.forEach(item => {
            const option = document.createElement('option');
            option.value = item['canonicalName'][0];
            dataList.appendChild(option);
        });
    }

    appendQueryResultMessage(result, messageElement) {
        let resultElement = messageElement.querySelector('.query-result');
        if (!resultElement) {
            resultElement = document.createElement('div');
            resultElement.classList.add('query-result');

            // Create a container for the header and content
            const resultHeader = document.createElement('div');
            resultHeader.classList.add('result-header');

            // Create the 'Copy Code' button
            const copyButton = document.createElement('button');
            copyButton.classList.add('copy-code-btn');
            copyButton.textContent = 'Copy Code';

            // Create the result content container
            const resultContent = document.createElement('div');
            resultContent.classList.add('result-content');

            // Event listener for 'Copy Code' button
            copyButton.addEventListener('click', () => {
                this.copyResultContent(resultContent);
            });

            resultHeader.appendChild(copyButton);

            // Create the toggle switch container
            const toggleContainer = document.createElement('div');
            toggleContainer.classList.add('toggle-container');

            // Create the label for the toggle switch
            const toggleLabel = document.createElement('label');
            toggleLabel.classList.add('toggle-switch');

            // Create the toggle switch input
            const toggleInput = document.createElement('input');
            toggleInput.type = 'checkbox';
            toggleInput.id = 'formatToggle' + Date.now(); // Unique ID

            // Create the slider span
            const sliderSpan = document.createElement('span');
            sliderSpan.classList.add('slider');

            // Append input and slider to label
            toggleLabel.appendChild(toggleInput);
            toggleLabel.appendChild(sliderSpan);

            // Create the text label
            const toggleText = document.createElement('span');
            toggleText.textContent = 'Display as CSV';

            // Append elements to toggle container
            toggleContainer.appendChild(toggleLabel);
            toggleContainer.appendChild(toggleText);

            // Append the toggle switch to the result header
            resultHeader.appendChild(toggleContainer);

            // Append the header and content to the result element
            resultElement.appendChild(resultHeader);
            resultElement.appendChild(resultContent);

            // Append the result element to the message element
            messageElement.appendChild(resultElement);

            // Now that resultContent is appended, we can call toggleResultFormat
            toggleInput.checked = this.userSettings.displayAsCSVEnabled;
            this.toggleResultFormat(result, resultElement, toggleInput.checked);

            // Event listener for the toggle switch
            toggleInput.addEventListener('change', () => {
                this.userSettings.displayAsCSVEnabled = toggleInput.checked;
                this.saveUserSettings();
                this.toggleResultFormat(result, resultElement, toggleInput.checked);
            });

        } else {
            // Clear previous content
            const resultContent = resultElement.querySelector('.result-content');
            resultContent.innerHTML = '';
        }

        const resultContent = resultElement.querySelector('.result-content');

        if (result.error) {
            resultContent.textContent = `An error occurred: ${result.error}`;
        } else {
            // Display the count
            const countElement = document.createElement('div');
            countElement.classList.add('result-count');
            countElement.textContent = `Number of objects returned: ${result.count}`;
            resultContent.appendChild(countElement);

            // Initially display the results as formatted JSON
            const preElement = document.createElement('pre');
            preElement.textContent = JSON.stringify(result.results, null, 2);
            resultContent.appendChild(preElement);
        }
    }

    copyResultContent(resultContent) {
        const textToCopy = resultContent.innerText;
        if (navigator.clipboard && window.isSecureContext) {
            // Modern asynchronous clipboard API
            navigator.clipboard.writeText(textToCopy).then(() => {
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        } else {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = textToCopy;
            textarea.style.position = 'fixed'; // Prevent scrolling to bottom
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();
            try {
                document.execCommand('copy');
                alert('Result copied to clipboard!');
            } catch (err) {
                console.error('Fallback: Oops, unable to copy', err);
            }
            document.body.removeChild(textarea);
        }
    }

    showLoading() {
        this.chatMessages.appendChild(this.loadingIndicator);
        this.scrollToBottom();
    }

    hideLoading() {
        if (this.chatMessages.contains(this.loadingIndicator)) {
            this.chatMessages.removeChild(this.loadingIndicator);
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    clearChatMessages() {
        this.messagesContainer.innerHTML = '';
    }

    populateChatThreads(threads) {
        this.chatList.innerHTML = '';
        threads.forEach(thread => {
            const threadItem = document.createElement('div');
            threadItem.classList.add('chat-thread-item');
            threadItem.dataset.threadId = thread.id;

            const threadTitle = document.createElement('span');
            threadTitle.classList.add('thread-title');
            threadTitle.textContent = thread.title;

            const editBtn = document.createElement('button');
            editBtn.classList.add('edit-chat-btn');
            editBtn.dataset.threadId = thread.id;
            editBtn.innerHTML = '&#9998;'; // Pencil icon

            const deleteBtn = document.createElement('button');
            deleteBtn.classList.add('delete-chat-btn');
            deleteBtn.dataset.threadId = thread.id;
            deleteBtn.innerHTML = '&times;'; // X symbol

            threadItem.appendChild(threadTitle);
            threadItem.appendChild(editBtn);
            threadItem.appendChild(deleteBtn);

            this.chatList.appendChild(threadItem);
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static getInstance() {
        if (!UIBinder.instance) {
            UIBinder.instance = new UIBinder();
        }
        return UIBinder.instance;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const app = App.getInstance();
    BaseAppUtils.initializeTooltips();
    if (app.uiBinder && app.uiBinder.autoRunToggle) {
        app.uiBinder.userSettings = app.uiBinder.loadUserSettings();
        app.uiBinder.initializeToggles();
    }
});

(function () {
    const app = App.getInstance();
    app.init();
})();

