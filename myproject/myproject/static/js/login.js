document.addEventListener("DOMContentLoaded", function () {
    const username = document.getElementById("username");
    const password = document.getElementById("password");
    const errorMessage = document.getElementById("error-message");
    const button = document.getElementById("send_data_button");

    button.addEventListener("click", function (event) {
        event.preventDefault();

        let errors = [];

        // Clear previous validation states
        username.classList.remove("is-invalid");
        password.classList.remove("is-invalid");

        if (username.value.trim().length == 0) {
            errors.push("Username must be filled.");
            username.classList.add("is-invalid");
        }

        if (password.value.trim().length == 0){
            errors.push("Password must be filled.");
            username.classList.add("is-invalid");
        }

        if (errors.length > 0) {
            errorMessage.innerHTML = errors.join("<br>");
            errorMessage.classList.remove("d-none");
        } else {
            errorMessage.classList.add("d-none");
            fetch(`/login`, {
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
                    let data = await response.json();
                    console.log(data);
                    // user_id, username, profile_pic, token
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
