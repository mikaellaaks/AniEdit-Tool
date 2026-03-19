document.getElementById('download-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const url = document.getElementById('episode-url').value;
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = 'Downloading...';
    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url})
        });
        if (response.ok) {
            statusDiv.textContent = 'Download started!';
        } else {
            statusDiv.textContent = 'Failed to start download.';
        }
    } catch (err) {
        statusDiv.textContent = 'Error: ' + err.message;
    }
});
