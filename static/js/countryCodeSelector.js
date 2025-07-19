document.addEventListener('DOMContentLoaded', () => {
  const select = document.getElementById('country_code');
  if (!select) return;

  const url = window.SelectConfig?.countryCodesUrl;
  if (!url) {
    console.error('Country codes URL not configured.');
    return;
  }

  fetch(url)
    .then(response => {
      if (!response.ok) throw new Error('Failed to load country codes JSON');
      return response.json();
    })
    .then(data => {
      data.forEach(({ code, name, dial_code}) => {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = `${name} (${dial_code})`;
        select.appendChild(option);
      });

      const initialValue = select.getAttribute('data-initial');
      if (initialValue) {
        select.value = initialValue;
      }
    })
    .catch(error => {
      console.error('Error loading country codes:', error);
    });
});
