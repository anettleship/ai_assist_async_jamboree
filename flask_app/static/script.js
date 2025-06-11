document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('tornadoForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const responseContent = document.getElementById('response-content');
    
    // Handle form submission for sync calls
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        callTornado('sync');
    });
    
    // Handle async button click
    document.querySelector('[data-action="async"]').addEventListener('click', function() {
        callTornado('async');
    });
    
    function callTornado(mode) {
        const endpoint = document.getElementById('endpoint').value;
        const url = mode === 'async' ? '/call-tornado-async' : '/call-tornado';
        
        // Show loading, hide results
        loading.style.display = 'block';
        results.style.display = 'none';
        
        // Prepare form data
        const formData = new FormData();
        formData.append('endpoint', endpoint);
        
        // Make the request
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displayResponse(data, mode);
        })
        .catch(error => {
            displayError(error, mode);
        })
        .finally(() => {
            loading.style.display = 'none';
        });
    }
    
    function displayResponse(data, mode) {
        let html = '';
        
        if (data.success) {
            html = `
                <div class="response-success">
                    <h6><i class="bi bi-check-circle"></i> Success (${mode.toUpperCase()})</h6>
                    <p class="mb-1"><strong>Status Code:</strong> <span class="response-code">${data.status_code}</span></p>
                    <p class="mb-1 url-called"><strong>URL Called:</strong> ${data.url_called}</p>
                    <div class="response-text">${escapeHtml(data.response_text)}</div>
                </div>
            `;
        } else {
            html = `
                <div class="response-error">
                    <h6><i class="bi bi-exclamation-triangle"></i> Error (${mode.toUpperCase()})</h6>
                    <p class="mb-0"><strong>Error:</strong> ${escapeHtml(data.error)}</p>
                </div>
            `;
        }
        
        responseContent.innerHTML = html;
        results.style.display = 'block';
    }
    
    function displayError(error, mode) {
        const html = `
            <div class="response-error">
                <h6><i class="bi bi-exclamation-triangle"></i> Network Error (${mode.toUpperCase()})</h6>
                <p class="mb-0"><strong>Error:</strong> ${escapeHtml(error.message)}</p>
            </div>
        `;
        
        responseContent.innerHTML = html;
        results.style.display = 'block';
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});