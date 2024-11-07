// Add a confirmation prompt for deleting an account
document.querySelector('form[onsubmit]').addEventListener('submit', function(event) {
    if (event.target.action.includes('delete_account')) {
        let confirmDelete = confirm("Are you sure you want to delete your account? This cannot be undone.");
        if (!confirmDelete) {
            event.preventDefault(); // Prevent form submission if user cancels
        }
    }
});

// Optional: Form validation before posting content
document.querySelector('form[action="/post"]')?.addEventListener('submit', function(event) {
    const content = document.querySelector('textarea[name="content"]');
    if (!content.value.trim()) {
        alert('Please write something before posting!');
        event.preventDefault(); // Prevent form submission if the content is empty
    }
});

// If you'd like to add any additional dynamic behavior, you can do it here
// For example, dynamically showing/hiding elements based on user interactions
