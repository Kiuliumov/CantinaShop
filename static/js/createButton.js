document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.create-btn').addEventListener('click', (e) => {
        e.preventDefault();

        localStorage.setItem('showSuccessModal', 'true');
        console.log(localStorage.getItem('showSuccessModal'));

        e.target.closest('form').submit();
    });
});