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
]

