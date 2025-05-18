from moviepy import VideoFileClip, concatenate_videoclips
import os
import random
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from datetime import datetime
import string
import ffmpeg
import time
import shutil
import subprocess


def is_overlapping(new_start, new_end, existing_ranges):
    for start, duration in existing_ranges:
        end = start + duration
        if not (new_end <= start or new_start >= end):
            return True
    return False



def create_directory_for_new_users(user_id):
    static_root = settings.STATICFILES_DIRS[0]
    test_dir_path = os.path.join(static_root, 'videos', str(user_id))
    os.makedirs(test_dir_path, exist_ok=True)



def save_video(video, user_id, ext): 
    try:
        static_root = settings.STATICFILES_DIRS[0]
        now = datetime.now()
        year = now.year
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

        video_url = f"{year}{month}{day}{user_id}{random_chars}"
        video_directory = os.path.join(static_root, 'videos', str(user_id), video_url)
        os.makedirs(video_directory, exist_ok=True)

        video_path = os.path.join(video_directory, f"{video_url}.{ext}")
        with open(video_path, 'wb+') as destination:
            for chunk in video.chunks():
                destination.write(chunk)

        result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0 or not result.stdout.strip():
            raise Exception(result.stderr.strip())

        duration = int(float(result.stdout.strip()))

        return {
            "status": True,
            "message": "Video stored.",
            "url_provided": video_url,
            "ext": ext,
            "duration": duration
        }

    except Exception as e:
        return {
            "status": False,
            "message": str(e),
            "message_to_user": "An error occurred."
        }
    
def create_thumbnail(video_file, user_id, ext):
    try:
        static_root = settings.STATICFILES_DIRS[0]
        # static_root / videos / {user_id} / video_url 
        video_path = os.path.join(static_root, 'videos', str(user_id), video_file, f"{video_file}.{ext}")
        output_path = os.path.join(static_root, 'videos', str(user_id), video_file, f"{video_file}.jpg") 
        for attempt in range(5):
            if os.path.exists(video_path):

                (
                    ffmpeg
                    .input(video_path, ss=1)
                    .output(output_path, vframes=1)
                    .run(capture_stdout=True, capture_stderr=True)
                )
                return {"status": True}
            else:
                time.sleep(0.5)
    except Exception.Error as e:
        return {"status": False, "message": str(e), "message_to_user": "An error occurred."}
    
def save_thumbnail(thumbnail, url, user_id, ext):
    try:
        static_root = settings.STATICFILES_DIRS[0]
        user_dir = os.path.join(static_root, 'videos', str(user_id), url)
        os.makedirs(user_dir, exist_ok=True)  # Ensure directory exists

        thumbnail_file_name = os.path.join(user_dir, f"{url}.{ext}")

        with open(thumbnail_file_name, 'wb+') as destination:
            for chunk in thumbnail.chunks():
                destination.write(chunk)

        return {"status": True}
    except Exception as e:
        return {
            "status": False,
            "message": str(e),
            "message_to_user": "An error occurred."
        }
    


def get_video_duration(file_path):
    try:
        result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0 or not result.stdout.strip():
            raise Exception(result.stderr.strip())

        return float(result.stdout.strip())  # duration in seconds

    except Exception as e:
        print("Error reading duration:", e)
        return None