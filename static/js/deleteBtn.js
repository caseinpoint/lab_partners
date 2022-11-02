for (let btn of document.querySelectorAll('.btn_delete')) {
    btn.addEventListener('click', (evt) => {
        const confirmed = confirm('Are you sure you want to delete this cohort? This cannot be undone.');
        if (!confirmed) {
            evt.preventDefault();
            return false;
        }
    });
}