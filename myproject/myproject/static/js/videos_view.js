document.addEventListener("DOMContentLoaded", () => {
    // GET THE LIKE AND DISLIKE VIDEO BUTTONS. 
    const video_like_buton = document.getElementById("video_like_buton");
    const video_dislike_buton = document.getElementById("video_dislike_buton");

    // IF USER IS LOGGED IT WILL GET THE USER LIKE OR DISLIKE STATUS
    if (is_user_logged()) {
        const token = localStorage.getItem("token");
        const user = JSON.parse(localStorage.getItem("user"));
        fetch(`/user_like_dislike_status?user_id=${user["user_id"]}&video_id=${received_video_id}`, {
            method: "GET"
        })
        .then(async response =>{
            if (response.status >= 500) {
                alert('An error occurred.');
            } 
            else if (response.status === 200) {
                let data = await response.json();
                like_dislike_status = data["like_dislike_status"];
                if (data["like_dislike_status"] == 'liked'){
                    video_like_buton.classList.remove("btn-outline-success");
                    video_like_buton.classList.add("btn-success");
                }
                else if (data["like_dislike_status"] == 'disliked') {
                    video_dislike_buton.classList.remove("btn-outline-danger");
                    video_dislike_buton.classList.add("btn-danger");
                }
            }
        });
    }


    // EVENT LISTENER WHEN USER CLICKS THE LIKE BUTTON 
    video_like_buton.addEventListener("click", function () {
        post_likes(received_video_id, "like");
    });


    // EVENT LISTENER WHEN USER CLICKS THE DISLIKE BUTTON 
    video_dislike_buton.addEventListener("click", function () {
        post_likes(received_video_id, "dislike");
    });
    function post_likes(video_id, is_like){
        // IF USER IS NOT LOGGED IT WILL REDIRECT THE USER TO THE LOGIN PAGE. 
        if (!is_user_logged()) {
            window.location.href = '/login';
        }

        const token = localStorage.getItem("token");
        const user = JSON.parse(localStorage.getItem("user"));

        fetch(`/post_likes/${is_like}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({user_id: user["user_id"], video_id: video_id})
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
                
                // REDIRECTS THE USER TO THE LOGIN PAGE IF THERE IS SOMETHING WRONG WITH THE USER'S TOKEN. 
                if (data["status"] == 401){
                    logout_user();
                    window.location.href = '/login';
                }

                // UPDATES THE LIKE AND DISLIKE BUTTONS
                like_dislike_status = data["like_status"];
                if (like_dislike_status == 'liked'){
                    video_like_buton.classList.remove("btn-outline-success");
                    video_like_buton.classList.add("btn-success");
                    video_dislike_buton.classList.remove("btn-danger");
                    video_dislike_buton.classList.add("btn-outline-danger");
                }
                else if (like_dislike_status == 'disliked'){
                    video_dislike_buton.classList.remove("btn-outline-danger");
                    video_dislike_buton.classList.add("btn-danger");
                    video_like_buton.classList.remove("btn-success");
                    video_like_buton.classList.add("btn-outline-success");
                }
                else if (like_dislike_status == ''){
                    video_like_buton.classList.remove("btn-success");
                    video_like_buton.classList.add("btn-outline-success");
                    video_dislike_buton.classList.remove("btn-danger");
                    video_dislike_buton.classList.add("btn-outline-danger");
                }
                
                // UPDATES THE NUMBER OF LIKES AND DISLIKES 
                // {"status": 200, "like_status": like_status, "new_likes": number_of_like_dislikes["likes"], "new_dislikes": number_of_like_dislikes["dislikes"] }
                video_like_buton.innerHTML = `Like ${data['new_likes']}`;
                video_dislike_buton.innerHTML = `Like ${data['new_dislikes']}`;  
            }
        })
        
    }
});