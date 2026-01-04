from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),

    # PROFILE
    path('profile/<str:pk>', views.profile, name='profile'),
    
    # FOLLOW / UNFOLLOW
    path('follow', views.follow, name='follow'),

    # SEARCH
    path('search', views.search, name='search'),

    # LIKE / UNLIKE
    path('like-post/', views.like_post, name='like-post'),

    # AUTH
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),

    # COMMENTAIRES
    path('add-comment/<str:post_id>/', views.add_comment, name='add-comment'),
    path('edit-comment/<int:comment_id>/', views.edit_comment, name='edit-comment'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete-comment'),

    # NOTIFICATIONS
    path('mark-notifications-as-seen/', views.mark_notifications_as_seen, name='mark-notifications-as-seen'),

    # MESSAGERIE
    path('chat/', views.chat_view, name='chat'),
    path('chat/<str:username>/', views.chat_view, name='chat-user'),
    path('send-message/', views.send_message, name='send-message'),
    path('get-messages/<str:username>/', views.get_messages, name='get-messages'),

    # RESSOURCES ACADÉMIQUES (EMPREINTE PERSONNELLE)
    path('save-resource/<uuid:post_id>/', views.save_resource, name='save-resource'),
]
