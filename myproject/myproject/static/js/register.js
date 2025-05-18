document.addEventListener("DOMContentLoaded", function () {
    console.log("JS is working");

    const button = document.getElementById("send_data_button");
    const form = document.querySelector("form");
    const username = document.getElementById("username");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirm_password");
    const errorMessage = document.getElementById("error-message");

    button.addEventListener("click", function (event) {
        event.preventDefault();

        let errors = [];

        // Clear previous validation states
        username.classList.remove("is-invalid");
        password.classList.remove("is-invalid");
        confirmPassword.classList.remove("is-invalid");

        // Validate username
        if (username.value.trim().length < 5) {
            errors.push("Username must be at least 5 characters long.");
            username.classList.add("is-invalid");
        }

        // Validate password
        if (password.value.length < 8) {
            errors.push("Password must be at least 8 characters long.");
            password.classList.add("is-invalid");
        }

        // Validate password confirmation
        if (password.value !== confirmPassword.value) {
            errors.push("Passwords do not match.");
            confirmPassword.classList.add("is-invalid");
        }

        if (errors.length > 0) {
            errorMessage.innerHTML = errors.join("<br>");
            errorMessage.classList.remove("d-none");
        } else {
            errorMessage.classList.add("d-none");
            fetch(`/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken() 
                },
                body: JSON.stringify({username: username.value, password: password.value})
            })
            .then(async response =>{
                if (!response.ok) {
                    let data = await response.json();
                    errors.push(data["message"]);
                    errorMessage.innerHTML = errors.join("<br>");
                    errorMessage.classList.remove("d-none");
                } 
                else if (response.status == 200) {
                    // user_id, username, profile_pic, token, 
                    let data = await response.json();
                    console.log(data);
                    const user_data = {
                        user_id: data["user_id"],
                        username: data["username"],
                        profile_pic: data["profile_pic"],
                    }
                    localStorage.setItem("token", data["token"]);
                    localStorage.setItem("user", JSON.stringify(user_data));
                    window.location.href = '/';
                }
            })
        }
    });
});
