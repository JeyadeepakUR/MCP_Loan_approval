// BFSI Loan Application - Frontend JavaScript

let sessionId = null;
let currentStage = 'SALES';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const startButton = document.getElementById('startButton');
const sessionInfo = document.getElementById('sessionInfo');
const stageBadge = document.getElementById('stageBadge');
const quickActions = document.getElementById('quickActions');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Start button
    startButton.addEventListener('click', startSession);

    // Send button
    sendButton.addEventListener('click', sendMessage);

    // Enter key to send
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !sendButton.disabled) {
            sendMessage();
        }
    });

    // Quick actions
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.dataset.message;
            sendMessage();
        });
    });
}

async function startSession() {
    showLoading(true);

    try {
        const response = await fetch('/api/start-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            sessionId = data.session_id;

            // Clear welcome message
            chatMessages.innerHTML = '';

            // Add system message
            addMessage('system', data.message);

            // Enable input
            userInput.disabled = false;
            sendButton.disabled = false;
            startButton.style.display = 'none';

            // Show session info
            sessionInfo.style.display = 'block';
            quickActions.style.display = 'flex';

            // Focus input
            userInput.focus();
        } else {
            showError('Failed to start session. Please try again.');
        }
    } catch (error) {
        showError('Connection error. Please check your internet connection.');
    } finally {
        showLoading(false);
    }
}

async function sendMessage() {
    const message = userInput.value.trim();

    if (!message || !sessionId) return;

    // Add user message to chat
    addMessage('user', message);

    // Clear input
    userInput.value = '';

    // Disable input while processing
    userInput.disabled = true;
    sendButton.disabled = true;

    showLoading(true);

    try {
        const response = await fetch('/api/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Add system response
            addMessage('system', data.message);

            // Update stage
            if (data.stage) {
                currentStage = data.stage;
                updateStageBadge(data.stage);
            }

            // Check if completed
            if (data.stage === 'COMPLETED') {
                showCompletionActions();
            } else if (data.stage === 'FAILED') {
                showFailureMessage();
            }
        } else {
            addMessage('system', '❌ ' + (data.error || 'An error occurred. Please try again.'));
        }
    } catch (error) {
        addMessage('system', '❌ Connection error. Please try again.');
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
        showLoading(false);
    }
}

function addMessage(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Format message with line breaks
    contentDiv.innerHTML = content.replace(/\n/g, '<br>');

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });

    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateStageBadge(stage) {
    stageBadge.textContent = stage;

    // Color coding
    stageBadge.className = 'session-badge';
    if (stage === 'COMPLETED') {
        stageBadge.classList.add('status-success');
    } else if (stage === 'FAILED') {
        stageBadge.classList.add('status-error');
    } else if (stage === 'UNDERWRITING') {
        stageBadge.classList.add('status-warning');
    }
}

function showCompletionActions() {
    // Hide quick actions
    quickActions.style.display = 'none';

    // Add download button
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'start-button';
    downloadBtn.innerHTML = '📄 Download Sanction Letter';
    downloadBtn.onclick = downloadSanctionLetter;

    document.querySelector('.input-container').appendChild(downloadBtn);

    // Disable further input
    userInput.disabled = true;
    sendButton.disabled = true;
}

function showFailureMessage() {
    quickActions.style.display = 'none';
    userInput.disabled = true;
    sendButton.disabled = true;
}

async function downloadSanctionLetter() {
    showLoading(true);

    try {
        const response = await fetch(`/api/download-sanction/${sessionId}`);

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sanction_letter_${sessionId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            addMessage('system', '✅ Sanction letter downloaded successfully!');
        } else {
            addMessage('system', '❌ Failed to download sanction letter.');
        }
    } catch (error) {
        addMessage('system', '❌ Error downloading file.');
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    if (show) {
        loadingOverlay.classList.add('active');
    } else {
        loadingOverlay.classList.remove('active');
    }
}

function showError(message) {
    addMessage('system', '❌ ' + message);
}
