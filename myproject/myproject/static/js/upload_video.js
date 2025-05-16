if (!is_user_logged()) {
    window.location.href = '/login';
}

document.addEventListener("DOMContentLoaded", ()=> {
    const token = localStorage.getItem("token");
    const upload_video_button = document.getElementById("upload_video_button");
    upload_video_button.addEventListener("click", (event)=> {
        event.preventDefault();

        let errors = [];
        const errorMessage = document.getElementById("error-message");

        const title_input = document.getElementById("title");
        const description_input = document.getElementById("description");
        const video_file_input = document.getElementById("video_file");
        const allowedExtensions = ['.mp4', '.avi', '.mkv'];

        const video_file = video_file_input.files[0];

        // Clear previous validation states
        video_file_input.classList.remove("is-invalid");
        title_input.classList.remove("is-invalid")

        if (title_input.value.trim().length == 0) {
            errors.push("Title must not be blank.");
            title_input.classList.add("is-invalid");
        }
      
        if (!video_file) {
            errors.push("Please select a video file..");
            video_file_input.classList.add("is-invalid");
        }

        else {
            const fileName = video_file.name;
            const extension = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase();
            if (!allowedExtensions.includes(`.${extension}`)){
                errors.push("Invalid file type.");
                video_file_input.classList.add("is-invalid");
            }
        }

        if (errors.length > 0) {
            errorMessage.innerHTML = errors.join("<br>");
            errorMessage.classList.remove("d-none");
        }
        else {
            const fileName = video_file.name;
            const extension = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase();
            errorMessage.classList.add("d-none");

            const formData = new FormData();
            formData.append('video', video_file);
            const user_id_on_cookie = JSON.parse(localStorage.getItem("user"))["user_id"];
            formData.append("user_id", user_id_on_cookie); 
            formData.append("title", title_input.value.trim()); 
            formData.append("description", description_input); 
            formData.append("extension", extension);
            fetch(`/upload_video`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    Authorization: `Bearer ${token}`
                },
                body: formData
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
                    window.location.href = `${data.url}`;
                }
            })
        }
    });
});