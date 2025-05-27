document.addEventListener("DOMContentLoaded", ()=> {
    const div_videos_users_followed = document.getElementById("div_videos_users_followed");

    if (is_user_logged()){
        const token = `Bearer ${localStorage.getItem("token")}`;

        fetch(`/get_sub_videos`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: token
            }
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
                let data = await response.json();
                div_videos_users_followed.innerHTML = "";
                if (data["videos"].length > 0) {
                    for (const video of data["videos"]) {
                        div_videos_users_followed.innerHTML += `
                            <div class="col">
                                <div class="card h-100">
                                    <a href="/videos/${video["video_id"]}">
                                    <img src="/static/videos/${video["user_id"]}/${video["video_id"]}/${video["thumbnail"]}" class="card-img-top" alt="Thumbnail" style="height: 180px; object-fit: cover;">
                                    </a>
                                    <div class="card-body">
                                    <h6 class="card-title">${video["title"]}</h6>
                                    <small class="text-muted">${video["video_views"]} views</small>
                                    </div>
                                </div>
                            </div>`;
                    }
                }
                else {
                    div_videos_users_followed.innerHTML = `<div class="alert alert-info text-center mt-4" role="alert">You are not following any users yet.</div>`;
                }
            }
        })
    
    }

});