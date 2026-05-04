let isRecording = false;
let isVideoActive = false;

function toggleVideo() {
    isVideoActive = !isVideoActive;
    const btn = event.target;
    if (isVideoActive) {
        btn.textContent = '⏸️ Stop Stream';
        addLog('Video stream started', 'success');
    } else {
        btn.textContent = '▶️ Start Stream';
        addLog('Video stream stopped', 'warning');
    }
}

function toggleRecording() {
    isRecording = !isRecording;
    const btn = event.target;
    if (isRecording) {
        btn.textContent = '⏹️ Stop Recording';
        btn.style.background = 'linear-gradient(135deg, var(--danger) 0%, #ff5252 100%)';
        addLog('Recording started', 'success');
    } else {
        btn.textContent = '⏹️ Record';
        btn.style.background = '';
        addLog('Recording stopped', 'warning');
    }
}

function triggerAlert() {
    const container = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger';
    alertDiv.innerHTML = `
        <span style="font-size: 1.2rem;">⚠️</span>
        <div>
            <strong>Alert Sent!</strong>
            <p style="font-size: 0.85rem; margin-top: 4px;">Threat notification sent to registered email.</p>
        </div>
    `;
    container.innerHTML = '';
    container.appendChild(alertDiv);
    addLog('Manual alert triggered - Email sent', 'success');

    setTimeout(() => {
        alertDiv.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => container.innerHTML = '', 300);
    }, 5000);
}

function saveSettings() {
    const email = document.getElementById('emailInput').value;
    const threshold = document.getElementById('thresholdInput').value;
    if (email) {
        addLog(`Settings saved - Email: ${email}, Threshold: ${threshold}`, 'success');
        const alert = document.getElementById('alertContainer');
        alert.innerHTML = `
            <div class="alert alert-success" style="margin-top: 15px;">
                <span>✓</span>
                <div>Settings saved successfully!</div>
            </div>
        `;
        setTimeout(() => alert.innerHTML = '', 3000);
    } else {
        addLog('Email address is required', 'error');
    }
}

function downloadLogs() {
    const logContent = document.getElementById('logDisplay').innerText;
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(logContent));
    element.setAttribute('download', 'system-logs.txt');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    addLog('Logs downloaded', 'success');
}

function addLog(message, type = 'info') {
    const logDisplay = document.getElementById('logDisplay');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    logDisplay.appendChild(entry);
    logDisplay.scrollTop = logDisplay.scrollHeight;
}
