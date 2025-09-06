// Wait for the HTML document to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {

    const loginForm = document.getElementById('login-form');
    const errorMessageDiv = document.getElementById('error-message');

    // Only add the event listener if the login form exists on this page
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            // 1. Prevent the default form submission (which reloads the page)
            event.preventDefault();

            // Clear any previous error messages
            errorMessageDiv.textContent = '';

            // 2. Get the values from the email and password input fields
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // 3. Create a URLSearchParams object for form data
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            try {
                // 4. Use fetch to make a POST request to our /auth/login endpoint
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: formData,
                });

                // 5. Check if the response is successful
                if (response.ok) {
                    // On success, parse the JSON to get the token
                    const data = await response.json();
                    
                    // Save the token to the browser's local storage
                    localStorage.setItem('accessToken', data.access_token);
                    
                    // Redirect to the recipes page
                    window.location.href = '/static/recipes.html';
                } else {
                    // On failure, parse the error response and display the message
                    const errorData = await response.json();
                    errorMessageDiv.textContent = errorData.detail || 'Login failed. Please try again.';
                }
            } catch (error) {
                // Handle network errors (e.g., server is down)
                errorMessageDiv.textContent = 'A network error occurred. Please try again later.';
                console.error('Login error:', error);
            }
        });
    }

    // We will add logic for other pages (like recipes.html) here later
});