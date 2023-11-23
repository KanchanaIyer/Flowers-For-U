window.onload = script
function script()
{
    const form = document.getElementById("login_form");
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        const data = {
            "username": username,
            "password": password,
        };

        const xhr = new XMLHttpRequest();
        xhr.open("POST", login_api_url, true);
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