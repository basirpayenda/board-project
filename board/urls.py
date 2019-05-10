from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'board'
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('<str:username>/update/',
         views.AccountUpdateView.as_view(), name='update_account'),
    path('board/<int:pk>/', views.TopicListView.as_view(), name='board_topics'),
    path('board/<int:pk>/new/', views.new_topic, name='new_topic'),

    path('board/<int:pk>/topic/<int:topic_pk>/',
         views.PostListView.as_view(), name='view_topic'),

    path('board/<int:pk>/topic/<int:topic_pk>/reply/',
         views.reply_topic, name='reply_topic'),

    path('board/<int:pk>/topic/<topic_pk>/post/<post_pk>/edit/',
         views.PostUpdateView.as_view(), name='edit_post')

]
