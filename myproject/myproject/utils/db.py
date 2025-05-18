import pyodbc
import os
from dotenv import load_dotenv
load_dotenv()
import random
import bcrypt
import myproject.utils.auth as myauth


db_password = os.environ.get('DB_PASSWORD')

# identify if it is running in an app service
if os.environ.get("WEBSITE_SITE_NAME"):
    print("Running in Azure App Service")
    connection_string = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=tcp:mysqltestpablitox.database.windows.net;"
        "Database=youtube_db;"
        "Authentication=ActiveDirectoryMsi;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

#identify if it is running on a VM
elif os.environ.get("COMPUTERNAME"):
    print(f"Running on a {os.environ.get('COMPUTERNAME')}")
    connection_string = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=mysqltestpablitox.database.windows.net;"
        "Database=youtube_db;"
        "Uid=pablitox;"
        f"Pwd={db_password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

#identify if it is running somewhere else    
else:
    print("Running locally or unknown")
    running_on = "vm"
    connection_string = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=mysqltestpablitox.database.windows.net;"
        "Database=youtube_db;"
        "Uid=pablitox;"
        f"Pwd={db_password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

def test_connection():
    try:
        conn = pyodbc.connect(connection_string)
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_connection():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return False

def inser_user_on_db(username, plain_text_password):
    if is_username_taken(username):
        print("User already taken")
        return {"result": False,"status": 400, "message": "Username is already in Use."}
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        hashed_pw = hashed_password(plain_text_password = plain_text_password)
        
        number = random.randint(1, 3)

        query = """
        INSERT INTO users (username, password, profile_pic)
        OUTPUT INSERTED.user_id
        VALUES (?, ?, ?)
        """
        data = (username, hashed_pw, f'default-{number}.jpg')

        cursor.execute(query, data)
        user_id = cursor.fetchone()[0]
        conn.commit()
        return {"result": True, "message": "Username added correctly.", "status": 200, "user_info": {"user_id": user_id, "profile_pic": f'default-{number}.jpg'}}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"result": False, "status": 500, "message": "An error occurred."}
    finally:
        if conn:
            conn.close()

def hashed_password(plain_text_password):
    salt = bcrypt.gensalt()
    encoded_pas = plain_text_password.encode('utf-8')
    return bcrypt.hashpw(encoded_pas, salt)

def is_username_taken(username):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM users
        WHERE LOWER(username) = LOWER(?)
        """

        cursor.execute(query, (username,))
        result_username_query = cursor.fetchall()
        return bool(result_username_query)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

def check_login(username, password):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        SELECT * FROM users
        WHERE LOWER(username) = LOWER(?)
        """

        cursor.execute(query, (username,))
        user_info = cursor.fetchone()
        conn.commit()

        if user_info == None:
            return {"result": False,"status": 400, "message": "username or password are incorrect!"}
        else:
            # (3, 'pablitox', '$2b$12$lWXJlcaslUj/xJY9Oy3V3unz13T.CJnhN4qebLYUzDTUUTxZTUV46', datetime.datetime(2025, 5, 13, 14, 14, 45, 167000), 'default-3.jpg')
            if myauth.are_passwords_the_same(plain_text_password=password, hashed_password=user_info[2]):
                return {"result": True, "message": "Username username and password are correct.", "status": 200, "user_info": {"user_id": user_info[0], "username": user_info[1], "profile_pic": user_info[4]}}
            else: 
                return {"result": False,"status": 400, "message": "username or password are incorrect!"}
    except Exception as e:
        print(f"Error: {e}")
        return {"result": False, "status": 500, "message": "An error occurred."}
    finally:
        if conn:
            conn.close()


def insert_video_on_db(video_id, user_id, title, descrition, thumbnail_ext, video_ext, duration):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO videos (video_id, user_id, thumbnail, video_file, title, description, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        data = (
            video_id,
            user_id,
            f"{video_id}.{thumbnail_ext}",
            f"{video_id}.{video_ext}",
            title,
            descrition,
            duration
        )

        cursor.execute(query, data)
        conn.commit()
        return {"result": True, "message": "video saved correctly", "status": 200}

    except Exception as e:
        return {
            "result": False,
            "status": 500,
            "message": str(e),
            "message_to_user": "An error occurred."
        }

    finally:
        if conn:
            conn.close()


def get_video_information_from_db(video_id):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT videos.*, users.username , users.profile_pic FROM videos
            JOIN users on videos.user_id = users.user_id
            WHERE video_id = ?;
        """

        cursor.execute(query, (video_id,))
        video_check_result = cursor.fetchone()
        conn.commit()
        if not video_check_result: 
            return {"result": False, "status": 404}
        if not video_check_result[11] in ["default-1.jpg", "default-2.jpg", "default-3.jpg"]:
            video_check_result[11] = "CUSTOM IMG"
        video_check_result[11] = f"/static/images/{video_check_result[11]}"
        # video = (video_id, user_id, likes, dislikes, thumbnail_file, title, video_file, description, duration, video_views, uploader_username, uploader_profile_pic)
        return {"result": True, "status": 200, "video": video_check_result}

    except Exception as e:
        return {
            "result": False,
            "status": 500,
            "message": str(e),
            "message_to_user": "An error occurred."
        }

    finally:
        if conn:
            conn.close()


def user_already_liked_video(user_id, video_id):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM video_likes
            WHERE user_id = ? AND video_id = ?
        """

        cursor.execute(query, (user_id, video_id))
        like_check_result = cursor.fetchone()
        conn.commit()
        if not like_check_result: 
            return {"result": False}
        
        # like_check_result = (user_id, video_id, 1_or_0 (True or False))
        return {"result": True, "status": like_check_result[2]}

    except Exception as e:
        return {
            "result": False,
            "status": 500,
            "message": str(e),
            "message_to_user": "An error occurred."
        }

    finally:
        if conn:
            conn.close()

def insert_like_on_db(user_id, video_id, is_like):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO video_likes (user_id, video_id, is_like)
            VALUES (?, ?, ?)
        """

        cursor.execute(query, (user_id, video_id, int(is_like)))
        conn.commit()
        return {"result": True}

    except Exception as e:
        return {
            "result": False,
            "status": 500,
            "message": str(e),
            "message_to_user": "An error occurred."
        }

    finally:
        if conn:
            conn.close()

def delete_like_on_db(user_id, video_id):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            DELETE FROM video_likes 
            where user_id = ? AND video_id = ?
        """

        cursor.execute(query, (user_id, video_id))
        conn.commit()
        return {"result": True}

    except Exception as e:
        return {
            "result": False,
            "status": 500,
            "message": str(e),
            "message_to_user": "An error occurred."
        }

    finally:
        if conn:
            conn.close()

def get_current_video_likes_dislikes(video_id):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                SUM(CASE WHEN is_like = 1 THEN 1 ELSE 0 END) AS likes,
                SUM(CASE WHEN is_like = 0 THEN 1 ELSE 0 END) AS dislikes
            FROM video_likes
            WHERE video_id = ?;
        """

        cursor.execute(query, (video_id,))
        current_likes = cursor.fetchone()
        conn.commit()
        return {"result": True, "likes": current_likes[0], "dislikes": current_likes[1]}

    except Exception as e:
        return {
            "result": False,
            "status": 500,
            "message": str(e),
            "message_to_user": "An error occurred."
        }

    finally:
        if conn:
            conn.close()


def has_user_liked_disliked_video(user_id, video_id):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM video_likes
            WHERE user_id = ? AND video_id = ?
        """

        cursor.execute(query, (user_id, video_id))
        user_like_dislike_status = cursor.fetchone()
        conn.commit()
        if not user_like_dislike_status:
            return {"result": True, "like_dislike_status": ""}
        
        like_dislike_status = "liked" if user_like_dislike_status[2] == 1 else "disliked"
        return {"result": True, "like_dislike_status": like_dislike_status}

    except Exception as e:
        return {
            "result": False,
            "status": 500,
            "message": str(e),
            "message_to_user": "An error occurred."
        }

    finally:
        if conn:
            conn.close()


def modify_video_like_dislike_from_db(user_id, video_id, new_like_status):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            UPDATE video_likes
            SET is_like = ?
            WHERE user_id = ? AND video_id = ?
        """

        cursor.execute(query, (new_like_status, user_id, video_id))
        conn.commit()
        return {"result": True}

    except Exception as e:
        return {
            "result": False,
            "status": 500,
            "message": str(e),
            "message_to_user": "An error occurred."
        }

    finally:
        if conn:
            conn.close()

 