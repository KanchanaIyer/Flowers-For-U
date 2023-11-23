
window.onload = script

function script() {
    const form = document.getElementById("register_form");
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        const confirm_password = document.getElementById("confirm_password").value;
        const email = document.getElementById("email").value;
        const confirm_email = document.getElementById("confirm_email").value;

        if (password !== confirm_password) { // Maybe we can do this with a listener on the confirm_password field?
            alert("Passwords do not match!");
            return;
        }
        if (email !== confirm_email) {  // Same here
            alert("Emails do not match!");
            return;
        }

        const data = {
            "username": username,
            "password": password,
            "email": email
        };

        const xhr = new XMLHttpRequest();
        xhr.open("POST", register_api_url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data));
        xhr.onload = function () {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response["status"] === "success") {
                    window.location.href = home_url;
                } else {
                    alert(response["message"]);
                }
            } else {
                alert("Error " + xhr.status + ": " + xhr.responseText);
            }
        }
    });
}