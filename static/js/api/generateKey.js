const button = document.getElementById('generateApiKeyBtn');
const resultDiv = document.getElementById('apiKeyResult');

button.addEventListener('click', async () => {
    resultDiv.textContent = 'Generating API key...';

    try {
        const response = await fetch(window.API_KEY_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include'
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || response.statusText || 'Failed to generate API key');
        }

        const data = await response.json();
        const expires = new Date(data.expires_at).toLocaleString();

        resultDiv.innerHTML = `
          <p><strong>API Key:</strong></p>
          <p class="text-indigo-400 break-all">${data.api_key}</p>
          <p class="mt-2 text-sm text-gray-400">Expires at: ${expires}</p>
          <p class="text-sm text-gray-400">User: ${data.user}</p>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<p class="text-red-500">${error.message}</p>`;
    }
});