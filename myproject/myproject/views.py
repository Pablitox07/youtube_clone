from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
import os
import json
import myproject.utils.db as mydb
import myproject.utils.auth as myauth
import myproject.utils.videos as videoandfs
from django.http import JsonResponse
from django.conf import settings
import logging


logger = logging.getLogger(__name__)



def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        received_username = data.get('username')
        received_password = data.get('password')
        result = mydb.inser_user_on_db(username= received_username, plain_text_password= received_password)
        if result["result"]:
            user_id = result["user_info"]["user_id"]
            profile_pic = result["user_info"]["profile_pic"]
            user_token = myauth.create_token(user_id, received_username, profile_pic)
            videoandfs.create_directory_for_new_users(user_id)
            return JsonResponse({ 
                "user_id": user_id,
                "username": received_username, 
                "profile_pic": profile_pic,
                "token": user_token
            }, status = result["status"])
        else: 
            return JsonResponse({
                "status": result["status"],
                "message": result["message"]
            }, status= result["status"])

    else:
        return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        received_username = data.get('username')
        received_password = data.get('password')
        # {"result": True, "message": "Username username and password are correct.", "status": 200, "user_info": {"user_id": user_info[0], "username": user_info[1], "profile_pic": user_info[4]}}
        result = mydb.check_login(username=received_username, password=received_password)
        if result["result"]:
            user_id = result["user_info"]["user_id"]
            profile_pic = result["user_info"]["profile_pic"]
            user_token = myauth.create_token(user_id, received_username, profile_pic)
            return JsonResponse({ 
                "user_id": user_id,
                "username": received_username, 
                "profile_pic": profile_pic,
                "token": user_token
            }, status = result["status"])
        else: 
            return JsonResponse({
                "status": result["status"],
                "message": result["message"]
            }, status= result["status"])
        
    else:
        return render(request, 'login.html')

def upload_video(request):
    if request.method == 'POST':
        # GET ALL INFORMATION FROM THE FETCH 
        auth_header = request.headers.get("Authorization")
        user_id_receved = request.POST.get('user_id')
        video_extension = request.POST.get('extension')
        video = request.FILES.get('video')
        thumbnail = request.FILES.get('thumbnail')
        thumbnail_ext = request.POST.get('thumbnail_ext')
        description = request.POST.get('description')
        video_title = str(request.POST.get('title'))

        # IF THERE IS NO THUMBNAIL EXT THEN WHEN THE THUMBNAIL IS CRETEED IT WILL ALWAYS BE JPG
        if not thumbnail_ext:
            thumbnail_ext = "jpg"

        # IF DESCRIPTION IS NOT PROVIDED MAKE IT AN EMPTY STR
        if not description:
            description = ""

        # CHECKS THAT THE VIDEO HAS BEEN SENT
        if not video:
            return JsonResponse({
                "status": 400,
                "message": "Error loading video. Please try again."
            }, status=400)

        # CHECK THAT TOKEN HAS BEEN SENT AND IF THE USER_ID WAS RECEIVED
        if not auth_header or not user_id_receved: 
            return JsonResponse({
                "status": 400,
                "message": "User not authenticated."
            }, status=400)
        
        # CHECKS THE TOKEN VALIDITY
        user_info = myauth.verify_token(token= auth_header)

        # CHECKS IF THE VALIDATION WAS SUCCESFULL AND IF THE USER_ID PROVIDED IN THE COOKIE CONSIDES WITH THE ONE IN THE TOKEN 
        if not user_info["status"] or int(user_info["user_id"]) != int(user_id_receved):
            return JsonResponse({
                "status": 401,
                "message": user_info["message"]
            }, status=401)
        
        # STORES THE VIDEO USING videos.py on the utils directory. It store the video on /static/videos/url_povided/url_provided.video_extension. 
        # It returns a directory with a status that says if it was able to store the video or not
        video_upload_result = videoandfs.save_video(video= video, user_id= user_info["user_id"],ext= video_extension)
        if not video_upload_result["status"]:
            logger.exception(video_upload_result["message"])
            return JsonResponse({
                "status": 500,
                "message": user_info["message_to_user"]
            }, status=500)
        
        # IF THE USER DOES NOT PROVIDES A THUMBNAIL IT WILL CREATE THE THUMBNAIL USING THE FIRST FRAME OF HE VIDEO.
        # It returns a directory with a status that says if it was able to CREATE THE THUMBNAIL or not
        if not thumbnail:
            gif_upload_result = videoandfs.create_thumbnail(video_file= video_upload_result["url_provided"], user_id= user_info["user_id"], ext= video_upload_result["ext"])
            if not gif_upload_result["status"]:
                logger.exception(video_upload_result["message"])
                return JsonResponse({
                    "status": 500,
                    "message": user_info["message_to_user"]
                }, status=500)
        
        #IF THE USER ACTUALLY PROVIDED A THUMBNAIL, IT WILL SAVE THE THUMBNAIL. 
        else:
            thumbnail_result = videoandfs.save_thumbnail(thumbnail= thumbnail, url= video_upload_result["url_provided"], user_id= user_info["user_id"], ext= thumbnail_ext)
            if not thumbnail_result["status"]:
                logger.exception(thumbnail_result["message"])
                return JsonResponse({
                    "status": 500,
                    "message": user_info["message_to_user"]
                }, status=500)
        
        # IF EVRYTHING GOES FINE. IT SHOULD GO AHEAD AND INSET THE VIDEO TO THE DATABASE.
        db_insert_video_result = mydb.insert_video_on_db(
            video_id= video_upload_result["url_provided"], 
            user_id= user_info["user_id"], 
            title= video_title, 
            descrition= str(description), 
            thumbnail_ext= str(thumbnail_ext), 
            video_ext= str(video_extension),
            duration= video_upload_result["duration"]
        )
        if not db_insert_video_result["result"]:
            logger.exception(thumbnail_result["message"])
            return JsonResponse({
                "status": 500,
                "message": user_info["message_to_user"]
            }, status=500)
        return JsonResponse({
                    "status": 200,
                    "url": f'/videos/{video_upload_result["url_provided"]}'
                }, status=200)


    else: 
        return render(request, 'upload_video.html')
    


def videos_view(request, video_id):
    result = mydb.get_video_information_from_db(video_id= video_id)
    # result["video"] = (video_id, user_id, likes, dislikes, thumbnail_file, title, video_file, description, duration, video_views, uploader_username, uploader_profile_pic)
    if int(result["status"]) == 404:
        print("400000000000000004") 
    
    # video_current_likes_dislikes = {"result": True, "likes": current_likes[0], "dislikes": current_likes[1]}
    video_current_likes_dislikes = mydb.get_current_video_likes_dislikes(video_id= video_id)
    if not video_current_likes_dislikes["result"]:
        logger.exception(video_current_likes_dislikes["message"])
        return JsonResponse({
            "status": 500,
            "message": video_current_likes_dislikes["message_to_user"]
        }, status=500)
    video_id = result["video"][0]
    user_id = result["video"][1] 
    likes = video_current_likes_dislikes["likes"]
    dislikes = video_current_likes_dislikes["dislikes"] 
    thumbnail_file = result["video"][4] 
    title =  result["video"][5]
    video_file = result["video"][6] 
    description = result["video"][7] 
    duration = result["video"][8]
    video_views = result["video"][9]
    uploader_username = result["video"][10]
    uploader_profile_pic = result["video"][11]

    return render(request, 'videos_view.html', 
        {
            "video_id": video_id,
            "user_id": user_id, 
            "likes": likes, 
            "dislikes": dislikes, 
            "thumbnail_file": thumbnail_file, 
            "title": title, 
            "video_file": video_file, 
            "description": description, 
            "duration": duration,
            "video_views": video_views,
            "video_path": f"/static/videos/{user_id}/{video_id}/{video_file}",
            "uploader_username": uploader_username,
            "uploader_profile_pic": uploader_profile_pic
        })



def post_likes(request, like_type):
    if request.method == 'POST':
        auth_header = request.headers.get("Authorization")
        data = json.loads(request.body)
        user_id_receved = data.get('user_id')
        video_id = data.get('video_id')

        # if like_type is equal to "like" then it needs to be a 1 in the database. else a 0. the database column i called is_like. 
        like_type = 1 if like_type == "like" else 0

        # CHECK THAT TOKEN HAS BEEN SENT AND IF THE USER_ID WAS RECEIVED
        if not auth_header or not user_id_receved: 
            return JsonResponse({
                "status": 400,
                "message": "User not authenticated."
            }, status=400)
        
        # CHECKS THE TOKEN VALIDITY
        # user_info = {"status": True, "user_id": user_id, "username": username, "profile_pic": profile_pic }
        user_info = myauth.verify_token(token= auth_header)

        # CHECKS IF THE VALIDATION WAS SUCCESFULL AND IF THE USER_ID PROVIDED IN THE COOKIE CONSIDES WITH THE ONE IN THE TOKEN 
        if not user_info["status"] or int(user_info["user_id"]) != int(user_id_receved):
            return JsonResponse({
                "status": 401,
                "message": user_info["message"]
            }, status=401)
        
        # like_status = {"result": True, "status": like_check_result[2]}
        like_status = mydb.user_already_liked_video(user_id= user_id_receved, video_id= video_id)

        # USER HAS NOT LIKED OR DISLIKED THE VIDEO. IT WILL INSERT IT INTO THE DATABASE  
        if not like_status["result"]:
            # IF FAILED. result_insert_like = { "result": False, "status": 500, "message": str(e), "message_to_user": "An error occurred."}
            # IF SUCCESS. result_insert_like ={ "result": True } 
            result_insert_like = mydb.insert_like_on_db(user_id= user_id_receved, video_id= video_id, is_like= int(like_type))

            # IF THERE IS AN EXCEPTION INSERTING THE LIKE OR DISLIKE IN THE DATABASE
            if not result_insert_like["result"]:
                logger.exception(result_insert_like["message"])
                return JsonResponse({
                    "status": 500,
                    "message": user_info["message_to_user"]
                }, status=500)
            # EVERYTHING WORKED INSERTING THE LIKE OR DISLIKE IN THE DATABASE. 
            else: 
                # GET THE CURRENT NUMBER OF LIKES AND DISLIKES. number_of_like_dislikes = {"result": True, "likes": current_likes[0], "dislikes": current_likes[1]}
                number_of_like_dislikes = mydb.get_current_video_likes_dislikes(video_id)
                # IF THERE IS AN EXCEPTION GETTING THE CURRENT NUMBER OF LIKES
                if not number_of_like_dislikes["result"]:
                    logger.exception(number_of_like_dislikes["message"])
                    return JsonResponse({
                        "status": 500,
                        "message": number_of_like_dislikes["message_to_user"]
                    }, status=500)
                
                like_status = 'liked' if like_type == 1 else 'disliked'
                return JsonResponse({
                "status": 200,
                "like_status": like_status,
                "new_likes": number_of_like_dislikes["likes"],
                "new_dislikes": number_of_like_dislikes["dislikes"]
            }, status=200)
        
        # IF THE USER LIKED OR DISLIKED THE VIDEO. 
        else: 
            # IF THE USER LIKED OR DISLIKED THE VIDEO AND THEY ARE TRYING TO LIKE THE VIDEO AGAIN, SO IT SHOULD DELETE THE CURRENT LIKE. THE SAME FOR DISLIKE
            if int(like_status["status"]) == int(like_type):
                result_delete_like = mydb.delete_like_on_db(user_id= user_id_receved, video_id= video_id)
                if not result_delete_like["result"]:
                    logger.exception(result_insert_like["message"])
                    return JsonResponse({
                        "status": 500,
                        "message": result_delete_like["message_to_user"]
                    }, status=500)
                #IF EVERYTHING WORKED DELETING THE LIKE OR DISLIKE ON THE DATABASE
                else:
                    # GET THE CURRENT NUMBER OF LIKES AND DISLIKES. number_of_like_dislikes = {"result": True, "likes": current_likes[0], "dislikes": current_likes[1]}
                    number_of_like_dislikes = mydb.get_current_video_likes_dislikes(video_id)
                    # IF THERE IS AN EXCEPTION GETTING THE CURRENT NUMBER OF LIKES
                    if not number_of_like_dislikes["result"]:
                        logger.exception(number_of_like_dislikes["message"])
                        return JsonResponse({
                            "status": 500,
                            "message": number_of_like_dislikes["message_to_user"]
                        }, status=500)
                    return JsonResponse({
                        "status": 200,
                        "like_status": "",                
                        "new_likes": number_of_like_dislikes["likes"],
                        "new_dislikes": number_of_like_dislikes["dislikes"]
                    }, status=200)

                
            # USER ALREADY LIKED OR DISLIKED THE VIDEO. THEY ARE TRYING TO LIKE A DISLIKED VIDEO OR DISLIKE A VIDEO LIKED VIDEO. 
            # IT SHOULD DELETE THE EXISTING LIKE OR DISLIKE FROM THE DATABASE
            result_like_modication = mydb.modify_video_like_dislike_from_db(user_id= user_id_receved, video_id= video_id, new_like_status= like_type)
            if not result_like_modication["result"]:
                logger.exception(result_like_modication["message"])
                return JsonResponse({
                    "status": 500,
                    "message": result_like_modication["message_to_user"]
                }, 
                status=500)
            # GET THE CURRENT NUMBER OF LIKES AND DISLIKES. number_of_like_dislikes = {"result": True, "likes": current_likes[0], "dislikes": current_likes[1]}
            number_of_like_dislikes = mydb.get_current_video_likes_dislikes(video_id)
            # IF THERE IS AN EXCEPTION GETTING THE CURRENT NUMBER OF LIKES
            if not number_of_like_dislikes["result"]:
                logger.exception(number_of_like_dislikes["message"])
                return JsonResponse({
                    "status": 500,
                        "message": number_of_like_dislikes["message_to_user"]
                }, status=500)
            like_status = 'liked' if like_type == 1 else 'disliked'
            return JsonResponse({
                "status": 200,
                "like_status": like_status,                        
                "new_likes": number_of_like_dislikes["likes"],
                "new_dislikes": number_of_like_dislikes["dislikes"]
            }, status=200)


def user_like_dislike_status(request):
    user_id_receved = request.GET.get('user_id')
    video_id = request.GET.get('video_id')
    # has_user_liked_disliked_video = {"result": True, "like_dislike_status": like_dislike_status}
    has_user_liked_disliked_video = mydb.has_user_liked_disliked_video(user_id= user_id_receved, video_id= video_id)

    if not has_user_liked_disliked_video["result"]:
        logger.exception(has_user_liked_disliked_video["message"])
        return JsonResponse({
            "status": 500,
            "message": has_user_liked_disliked_video["message_to_user"]
        }, 
        status=500)
    return JsonResponse({
        "status": 200,
        "like_dislike_status": has_user_liked_disliked_video["like_dislike_status"]
    }, 
    status=200)
