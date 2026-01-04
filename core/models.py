# from django.db import models
# from django.contrib.auth import get_user_model
# import uuid

# User = get_user_model()

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     id_user = models.IntegerField()
#     bio = models.TextField(blank=True)
#     profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
#     location = models.CharField(max_length=100, blank=True)

#     def __str__(self):
#         return self.user.username


# class Post(models.Model):
#     CATEGORY_CHOICES = (
#         ('general', 'Général'),
#         ('math', 'Mathématiques'),
#         ('cs', 'Informatique'),
#         ('physics', 'Physique'),
#         ('bio', 'Biologie'),
#         ('other', 'Autre'),
#     )

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
#     image = models.ImageField(upload_to='post_images')
#     caption = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     no_of_likes = models.IntegerField(default=0)
    
#     # NOUVEAUX CHAMPS POUR L'EMPREINTE PERSONNALISÉE
#     is_resource = models.BooleanField(default=False) # Si c'est un document/cours
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')

#     def __str__(self):
#         return f"Post by {self.user.username} - {self.category}"


# class LikePost(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('post', 'user')

#     def __str__(self):
#         return f"{self.user.username} likes {self.post.id}"


# class FollowersCount(models.Model):
#     follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')

#     def __str__(self):
#         return f"{self.follower.username} follows {self.user.username}"
    
# class Comment(models.Model):
#     post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.text[:20]}"

# class Notification(models.Model):
#     NOTIFICATION_TYPES = (
#         ('like', 'Like'),
#         ('comment', 'Comment'),
#         ('follow', 'Follow'),
#     )
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_sender')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_receiver')
#     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
#     text_preview = models.CharField(max_length=255, blank=True)
#     is_seen = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

# class Message(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     content = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         ordering = ['created_at']

# # MODÈLE POUR LA BIBLIOTHÈQUE PERSONNELLE
# class SavedResource(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     saved_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'post')






from django.db import models
from django.contrib.auth import get_user_model
import uuid
import os

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'Général'),
        ('math', 'Mathématiques'),
        ('cs', 'Informatique'),
        ('physics', 'Physique'),
        ('bio', 'Biologie'),
        ('other', 'Autre'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    # CHANGEMENT : Utilisation de FileField pour accepter tout type de fichier
    file = models.FileField(upload_to='post_files')
    
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    no_of_likes = models.IntegerField(default=0)
    is_resource = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')

    def __str__(self):
        return f"Post by {self.user.username} - {self.category}"

    @property
    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()

    @property
    def is_video(self):
        return self.extension in ['.mp4', '.webm', '.ogg']

    @property
    def is_image(self):
        return self.extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    @property
    def is_pdf(self):
        return self.extension == '.pdf'


class LikePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('post', 'user')

class FollowersCount(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_sender')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_receiver')
    notification_type = models.CharField(max_length=20)
    text_preview = models.CharField(max_length=255, blank=True)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at']

class SavedResource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'post')
