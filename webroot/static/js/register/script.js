
window.onload = script

function script() {
    const register_form = document.getElementById("register_form");
    const error_message = document.getElementById("error_message");
    register_form.addEventListener("submit", function (event) {
        event.preventDefault();
        let target = event.target;
        //Before we send the data to the server, we should check if the passwords and emails match and then remove the confirm_password and confirm_email fields from the data object
        const username = target.username.value;
        const password = target.password.value;
        const confirm_password = target.confirm_password.value;
        const email = target.email.value;
        const confirm_email = target.confirm_email.value;
        const redirect_url = target.redirect_url.value;

        if (password !== confirm_password) { // Maybe we can do this with a listener on the confirm_password field?
            error_message.innerHTML = "Passwords do not match!";
            return;
        }
        if (email !== confirm_email) {  // Same here
            error_message.innerHTML = "Emails do not match!";
            return;
        }
        // If we get here, we can send the data to the server as a POST request with the www-form-urlencoded content type

        const form_data = new FormData();
        form_data.append("username", username);
        form_data.append("password", password);
        form_data.append("email", email);
        form_data.append("redirect_url", redirect_url);
        const request = new Request(register_url, {
            method: "POST",
            body: form_data,
        });

        // Load the response from the server which is a flask redirect to the redirect_url or render_template("register.html") with an error message
        fetch(request).then(function (response) {
            return response.text();
        }).then(function (text) {
            document.open();
            document.write(text);
            document.close();
        }).catch(function (error) {
            console.log(error);
        });

    });
}