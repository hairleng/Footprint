from django.urls import path
from socialnetwork import views
from django.contrib import admin

urlpatterns = [
    path('add-comment', views.add_comment),
    path('get-logs', views.get_logs),
    path('get-logs', views.get_logs),
    path('get-bookmark-logs', views.get_bookmark_logs),
    path('get-user-logs/<int:user_id>', views.get_user_logs),
    path('filter-date', views.filter_date, name='filter_date'),
    path('profile', views.home),
    path('like-log', views.like_log),
    path('unlike-log', views.unlike_log),
    path('bookmark', views.add_bookmark),
    path('get-one-log/<int:log_id>', views.get_one_log, name='get_one_log'),
    path('unbookmark', views.remove_bookmark),
    path('ajax-follow', views.ajax_follow),
    path('ajax-unfollow', views.ajax_unfollow),
]
