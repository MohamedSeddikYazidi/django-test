from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Comment, Notification, Message, SavedResource
from django.db.models import Q
from itertools import chain
import random

# --- UTILITAIRES ---
def create_notification(sender, user, notification_type, post=None, text_preview=""):
    if sender != user:
        Notification.objects.create(sender=sender, user=user, notification_type=notification_type, post=post, text_preview=text_preview)

def get_navbar_context(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_notifications_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    unread_messages_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    user_profile = Profile.objects.get(user=request.user)
    return {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'unread_messages_count': unread_messages_count,
        'user_profile': user_profile,
        'categories': Post.CATEGORY_CHOICES
    }

# --- VUES PRINCIPALES ---
@login_required(login_url='signin')
def index(request):
    category = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    user_following_ids = FollowersCount.objects.filter(follower=request.user).values_list('user', flat=True)
    
    posts = Post.objects.all()
    if search_query:
        posts = posts.filter(Q(caption__icontains=search_query) | Q(user__username__icontains=search_query))
    if category != 'all':
        posts = posts.filter(category=category)
    elif not search_query:
        posts = posts.filter(user__id__in=list(user_following_ids) + [request.user.id])
    
    feed_list = posts.order_by('-created_at')
    user_liked_post_ids = LikePost.objects.filter(user=request.user).values_list('post_id', flat=True)
    user_saved_post_ids = SavedResource.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    for post in feed_list:
        post.is_liked = post.id in user_liked_post_ids
        post.is_saved = post.id in user_saved_post_ids

    suggestions = User.objects.exclude(id=request.user.id).exclude(id__in=user_following_ids)
    suggestion_profiles = Profile.objects.filter(user__in=suggestions).order_by('?')[:4]
    
    context = get_navbar_context(request)
    context.update({
        'posts': feed_list,
        'suggestions_username_profile_list': suggestion_profiles,
        'current_category': category,
        'search_query': search_query
    })
    return render(request, 'index.html', context)

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user
        file = request.FILES.get('file_upload')
        caption = request.POST.get('caption', '')
        category = request.POST.get('category', 'general')
        is_resource = request.POST.get('is_resource') == 'on'
        if file:
            Post.objects.create(user=user, file=file, caption=caption, category=category, is_resource=is_resource)
            messages.success(request, "Publication partagée !")
    return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile_target = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object).order_by('-created_at')
    saved_resources = SavedResource.objects.filter(user=request.user).select_related('post')
    
    user_liked_post_ids = LikePost.objects.filter(user=request.user).values_list('post_id', flat=True)
    user_saved_post_ids = SavedResource.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    for post in user_posts:
        post.is_liked = post.id in user_liked_post_ids
        post.is_saved = post.id in user_saved_post_ids
    
    is_following = FollowersCount.objects.filter(follower=request.user, user=user_object).exists()
    context = get_navbar_context(request)
    context.update({
        'user_object': user_object,
        'user_profile_target': user_profile_target,
        'user_posts': user_posts,
        'saved_resources': saved_resources,
        'user_post_length': user_posts.count(),
        'button_text': 'Unfollow' if is_following else 'Follow',
        'user_followers': FollowersCount.objects.filter(user=user_object).count(),
        'user_following': FollowersCount.objects.filter(follower=user_object).count(),
    })
    return render(request, 'profile.html', context)

# --- COMMENTAIRES ---
@login_required(login_url='signin')
def add_comment(request, post_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            post = get_object_or_404(Post, id=post_id)
            Comment.objects.create(post=post, user=request.user, text=comment_text)
            create_notification(request.user, post.user, 'comment', post=post, text_preview=comment_text[:50])
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='signin')
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user and request.method == 'POST':
        comment.text = request.POST.get('comment_text')
        comment.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='signin')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        comment.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

# --- INTERACTIONS ---
@login_required(login_url='signin')
def like_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        like_filter = LikePost.objects.filter(post=post, user=request.user).first()
        if like_filter:
            like_filter.delete()
            if post.no_of_likes > 0: post.no_of_likes -= 1
            liked = False
        else:
            LikePost.objects.create(post=post, user=request.user)
            post.no_of_likes += 1
            liked = True
            create_notification(request.user, post.user, 'like', post=post)
        post.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'liked': liked, 'count': post.no_of_likes})
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='signin')
def save_resource(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    saved_item, created = SavedResource.objects.get_or_create(user=request.user, post=post)
    if not created:
        saved_item.delete()
        saved = False
    else:
        saved = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'saved': saved})
    return redirect(request.META.get('HTTP_REFERER', '/'))

# --- MESSAGERIE ---
@login_required(login_url='signin')
def chat_view(request, username=None):
    context = get_navbar_context(request)
    messages_query = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('-created_at')
    chat_users_ids = []
    for msg in messages_query:
        other_user_id = msg.receiver_id if msg.sender_id == request.user.id else msg.sender_id
        if other_user_id not in chat_users_ids: chat_users_ids.append(other_user_id)
    
    from django.db.models import Case, When
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(chat_users_ids)])
    chat_users = User.objects.filter(id__in=chat_users_ids).order_by(preserved)
    
    active_chat_user = None
    messages_list = []
    if username:
        active_chat_user = get_object_or_404(User, username=username)
        Message.objects.filter(sender=active_chat_user, receiver=request.user, is_read=False).update(is_read=True)
        messages_list = Message.objects.filter((Q(sender=request.user) & Q(receiver=active_chat_user)) | (Q(sender=active_chat_user) & Q(receiver=request.user))).order_by('created_at')
    
    context.update({'chat_users': chat_users, 'active_chat_user': active_chat_user, 'messages_list': messages_list})
    return render(request, 'chat.html', context)

@login_required(login_url='signin')
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        receiver = get_object_or_404(User, id=receiver_id)
        if content:
            message = Message.objects.create(sender=request.user, receiver=receiver, content=content)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'sent', 'content': message.content, 'created_at': 'Just now'})
    return redirect('/chat')

@login_required(login_url='signin')
def get_messages(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = Message.objects.filter((Q(sender=request.user) & Q(receiver=other_user)) | (Q(sender=other_user) & Q(receiver=request.user))).order_by('created_at')
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    messages_data = [{'sender': msg.sender.username, 'content': msg.content, 'created_at': msg.created_at.strftime("%H:%M")} for msg in messages]
    return JsonResponse({'messages': messages_data})

# --- AUTRES ---
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower_username = request.POST.get('follower')
        user_to_follow_username = request.POST.get('user')
        follower_obj = get_object_or_404(User, username=follower_username)
        user_to_follow_obj = get_object_or_404(User, username=user_to_follow_username)
        check_follower = FollowersCount.objects.filter(follower=follower_obj, user=user_to_follow_obj).first()
        if check_follower is None:
            FollowersCount.objects.create(follower=follower_obj, user=user_to_follow_obj)
            create_notification(follower_obj, user_to_follow_obj, 'follow')
        else:
            check_follower.delete()
        return redirect('/profile/' + user_to_follow_username)
    return redirect('/')

@login_required(login_url='signin')
def mark_notifications_as_seen(request):
    Notification.objects.filter(user=request.user, is_seen=False).update(is_seen=True)
    return JsonResponse({'status': 'success'})

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        user_profile.bio = request.POST.get('bio', user_profile.bio)
        user_profile.location = request.POST.get('location', user_profile.location)
        if request.FILES.get('image'): user_profile.profileimg = request.FILES.get('image')
        user_profile.save()
        return redirect('settings')
    context = get_navbar_context(request)
    return render(request, 'setting.html', context)

@login_required(login_url='signin')
def search(request):
    username_profile_list = []
    if request.method == 'POST':
        username = request.POST.get('username', '')
        users = User.objects.filter(username__icontains=username)
        username_profile_list = Profile.objects.filter(user__in=users)
    context = get_navbar_context(request)
    context.update({'username_profile_list': username_profile_list})
    return render(request, 'search.html', context)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if password == request.POST['password2']:
            if not User.objects.filter(email=email).exists() and not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                auth.login(request, user)
                Profile.objects.create(user=user, id_user=user.id)
                return redirect('settings')
        messages.info(request, 'Invalid details')
        return redirect('signup')
    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            auth.login(request, user)
            return redirect('/')
        messages.info(request, 'Invalid Credentials')
    return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')