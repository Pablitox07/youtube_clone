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
                "status": 400,
                "message": user_info["message"]
            }, status=400)
        
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
            video_ext= str(video_extension)
        )
        if not db_insert_video_result["result"]:
            logger.exception(thumbnail_result["message"])
            return JsonResponse({
                "status": 500,
                "message": user_info["message_to_user"]
            }, status=500)
        return JsonResponse({
                    "status": 200,
                    "url": f'/static/videos/{user_info["user_id"]}/{video_upload_result["url_provided"]}/{video_upload_result["url_provided"]}.{video_upload_result["ext"]}'
                }, status=200)


    else: 
        return render(request, 'upload_video.html')
    


def videos_view(request):
    return render(request, 'videos_view.html')