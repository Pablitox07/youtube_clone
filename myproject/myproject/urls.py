from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('register', views.register_view, name='register'),        
    path('login', views.login_view, name='login'),                  
    path('upload_video', views.upload_video, name='upload_video'),   
    path('videos/<str:video_id>/', views.videos_view, name='video_detail'),
    path('post_likes/<str:like_type>/', views.post_likes, name='post_likes'),
    path('user_like_dislike_status', views.user_like_dislike_status, name= 'user_like_dislike_status'),
    path('check_token', views.check_token, name= 'check_token'),
    path('publish_comment', views.publish_comment, name= 'publish_comment'),
    path('publish_comment_likes', views.publish_comment_likes, name= 'publish_comment_likes'),
    path('search_results', views.search_results, name= "search_results"),
    path('profile/<str:user_id>/', views.profile_page, name= 'profile_page'),
    path('is_user_following_the_other', views.is_user_following_the_other, name= "is_user_following_the_other"),
    path('follow_user', views.follow_user, name= "follow_user")
]

