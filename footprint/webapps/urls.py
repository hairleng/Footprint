"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import notifications
from django.contrib import admin
from django.urls import path, include, re_path
from socialnetwork import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    # path('register', views.register_action, name='register'),
    # path('login', views.login_action, name='login'),
    path('global_stream', views.home, name='home'),
    path('user_profile', views.user_profile, name='user_profile'),
    # path('logout', views.logout_action, name='logout'),
    path('travel_stream', views.travel_stream, name="travel_stream"),
    path('filtered_stream', views.filtered_stream, name="filtered_stream"),
    path('bookmark_stream',views.bookmark_stream, name="bookmark_stream"),
    path('user_stream/<int:user_id>',views.show_all_user_stream, name="show_all_user_stream"),
    path('add_profile', views.add_profile, name='add_profile'),
    path('get_photo/<int:id>', views.get_photo, name='get_photo'),
    path('get_profile/<username>', views.get_profile, name='get_profile'),
    path('one_log/<int:log_id>/', views.one_log, name='one_log'),
    path('follow/<int:id>', views.follow, name='follow'),
    path('unfollow/<int:id>', views.unfollow, name='unfollow'),
    path('socialnetwork/', include('socialnetwork.urls')),
    path('accounts/', include('allauth.urls')),
    path('log_editor', views.log_editor, name="log_editor"),
    path('log_display', views.log_display, name="log_display"),
    path('add_log/<int:log_id>', views.add_log, name="add_log"),
    path('edit_log/<int:log_id>', views.edit_log, name="edit_log"),
    path('get_picture/<int:log_id>', views.get_picture, name="get_picture"),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('my_notifications', views.my_notifications, name='my_notifications'),
    path('mark_as_read', views.mark_as_read_action, name='mark_as_read'),
    path('about', views.about, name='about')
]
