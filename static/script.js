// Update detection count
function updateDetectionData() {
    fetch('/detection_data')
        .then(response => response.json())
        .then(data => {
            // Update detection count
            document.getElementById('detection-count').textContent = data.detections;
            
            // Update FPS
            if (data.fps) {
                document.getElementById('frame-rate').textContent = data.fps.toFixed(1);
                document.querySelector('#fps-counter span').textContent = `${data.fps.toFixed(1)} FPS`;
            }
            
            // Add new detections to log
            if (data.new_detections && data.new_detections.length > 0) {
                const logContainer = document.getElementById('log-items');
                data.new_detections.forEach(detection => {
                    const logItem = document.createElement('div');
                    logItem.className = 'log-item';
                    logItem.innerHTML = `
                        <div class="log-icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="log-content">
                            <div class="log-message">Pothole detected (${detection.size})</div>
                            <div class="log-time">${new Date().toLocaleTimeString()}</div>
                        </div>
                        <div class="log-confidence">${(detection.confidence * 100).toFixed(1)}%</div>
                    `;
                    logContainer.insertBefore(logItem, logContainer.firstChild);
                    
                    // Limit log items to 50
                    if (logContainer.children.length > 50) {
                        logContainer.removeChild(logContainer.lastChild);
                    }
                });
            }
        })
        .catch(error => console.error('Error fetching detection data:', error));
}

// Clear log
document.getElementById('clear-log').addEventListener('click', () => {
    const logContainer = document.getElementById('log-items');
    logContainer.innerHTML = `
        <div class="log-item">
            <div class="log-icon">
                <i class="fas fa-info-circle"></i>
            </div>
            <div class="log-content">
                <div class="log-message">Log cleared</div>
                <div class="log-time">${new Date().toLocaleTimeString()}</div>
            </div>
        </div>
    `;
});

// Export log (placeholder functionality)
document.getElementById('export-log').addEventListener('click', () => {
    const logItem = document.createElement('div');
    logItem.className = 'log-item';
    logItem.innerHTML = `
        <div class="log-icon">
            <i class="fas fa-info-circle"></i>
        </div>
        <div class="log-content">
            <div class="log-message">Export functionality would be implemented here</div>
            <div class="log-time">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    document.getElementById('log-items').insertBefore(logItem, document.getElementById('log-items').firstChild);
});

// Update data every second
setInterval(updateDetectionData, 1000);

// Initial update
updateDetectionData();