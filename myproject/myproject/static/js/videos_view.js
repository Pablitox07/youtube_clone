document.addEventListener("DOMContentLoaded", () => {
    // GET THE LIKE AND DISLIKE VIDEO BUTTONS. 
    const video_like_buton = document.getElementById("video_like_buton");
    const video_dislike_buton = document.getElementById("video_dislike_buton");
    const publish_comment_button = document.getElementById('publish_comment_button');
    const errorMessage = document.getElementById("error-message");
    const comment_seccion_ul = document.getElementById('comment_seccion_ul');
    const follow_profile_button = document.getElementById("follow_profile_button");


    // IF USER IS LOGGED IT WILL GET THE USER LIKE OR DISLIKE STATUS
    if (is_user_logged()) {
        const token = localStorage.getItem("token");
        const user = JSON.parse(localStorage.getItem("user"));
        fetch(`/user_like_dislike_status?user_id=${user["user_id"]}&video_id=${received_video_id}&uploader=${received_user_id}`, {
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

                data["user_comments_likes_status"].forEach(function(comment) {
                    let comment_like_buton = document.getElementById(`like_button_commnet_id_${comment[1]}`);
                    let comment_dislike_buton = document.getElementById(`dislike_button_commnet_id_${comment[1]}`);
                    if (comment[2]){
                        comment_like_buton.classList.remove("btn-outline-success");
                        comment_like_buton.classList.add("btn-success");
                        comment_dislike_buton.classList.remove("btn-danger");
                        comment_dislike_buton.classList.add("btn-outline-danger");
                    }
                    else {
                        comment_dislike_buton.classList.remove("btn-outline-danger");
                        comment_dislike_buton.classList.add("btn-danger");
                        comment_like_buton.classList.remove("btn-success");
                        comment_like_buton.classList.add("btn-outline-success");
                    }
                  });
                
                if (data["own_video"]){
                    follow_profile_button.classList.add("d-none");
                }
                if (data["follwoing_state"]){
                    follow_profile_button.innerHTML = "Following";
                }
                else{
                    follow_profile_button.innerHTML = "Follow";
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
                // REDIRECTS THE USER TO THE LOGIN PAGE IF THERE IS SOMETHING WRONG WITH THE USER'S TOKEN. 
                if (data["status"] == 401){
                    logout_user();
                    window.location.href = '/login';
                }
            } 
            else if (response.status == 200) {
                // user_id, username, profile_pic, token, 
                let data = await response.json();
                console.log(data);
                
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
                video_like_buton.innerHTML = `Like (${data['new_likes']})`;
                video_dislike_buton.innerHTML = `Dislike (${data['new_dislikes']})`;  
            }
        })
        
    }

    // EVENT LSITINER FOR THE VIDEO COMMENT  
    publish_comment_button.addEventListener("click", ()=> {
        const comment_text_are = document.getElementById('comment_text_are');

        let errors = [];
        // Clear previous validation states
        comment_text_are.classList.remove("is-invalid");

        // COMMNET CANNOT BE EMPTY
        if (comment_text_are.value.trim().length === 0) {
            errors.push("Comment must not be blank.");
            comment_text_are.classList.add("is-invalid");
        }

        // IF THERE ARE ERRORS 
        if (errors.length > 0) {
            errorMessage.innerHTML = errors.join("<br>");
            errorMessage.classList.remove("d-none");
            return;
        }

        const user_id = JSON.parse(localStorage.getItem("user"));
        fetch(`/publish_comment`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
            Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({user_id: user_id['user_id'], comment_content: comment_text_are.value.trim(), video_id: received_video_id})
        })
        .then(async response =>{
            if (!response.ok) {
                let data = await response.json();
                alert(data["message"]);
            } 
            else if (response.status == 401) {
                logout_user();
                window.location.href = "/login";
            }
            else if (response.status == 200) {
                // user_id, username, profile_pic, token, 
                let data = await response.json();
                console.log(data);
                const li = document.createElement("li");
                li.classList.add("list-group-item");
                li.innerHTML= 
                `<div class="d-flex align-items-start"> 
                <!-- Profile Picture -->
                <img src="/static/images/${user_id['profile_pic']}" alt="Profile" class="rounded-circle me-3" width="40" height="40">
        
                <div class="flex-grow-1">
                  <!-- Username and Date -->
                  <div class="d-flex justify-content-between">
                    <strong>${user_id['username']}</strong>
                    <small class="text-muted">${data['created_on']}</small>
                  </div>
        
                  <!-- Comment Text -->
                  <span>${comment_text_are.value.trim()}</span>
        
                  <!-- Like/Dislike Buttons -->
                  <div class="mt-2 d-flex align-items-center gap-2">
                    <button class="btn btn-sm btn-outline-success" onclick="comment_likes(${data['comment_id']}, ${true})" id="like_button_commnet_id_${data['comment_id']}">Like (0)</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="comment_likes(${data['comment_id']}, ${false})" id="dislike_button_commnet_id_${data['comment_id']}">Dislike (0)</button>
                  </div>
                </div>
              </div>
              `;
              comment_seccion_ul.appendChild(li);
              const comment_text_when_no_comments = document.getElementById("comment_text_when_no_comments");
              if (comment_text_when_no_comments) {
                comment_text_when_no_comments.classList.add("d-none");
              }
            }
        })

    });

    follow_profile_button.addEventListener("click", ()=>{
        if (is_user_logged()) {
            const token = localStorage.getItem("token");
            fetch("/follow_user", {
                  method: "POST",
                  headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Authorization": `Bearer ${token}`
                  },
                  body: JSON.stringify({user_profile:received_user_id})
            })
            .then(async response =>{
                  if (!response.ok) {
                      alert('An error occurred.');
                  } 
                  else {
                      let data = await response.json();
                      console.log(data);
                      if (data["follwoing_state"]){
                        follow_profile_button.innerHTML = "Following";
                      }
                      else {
                        follow_profile_button.innerHTML = "Follow";
                      }
                  }
            });
          }
          else {
            window.location.href = '/login';
          }
    });


    
});