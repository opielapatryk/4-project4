from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Post, User, Likes
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

# Functions
def pagination(request, current_user,posts_list):
    for post in posts_list:
        post.likes_count = Likes.objects.filter(post=post).count() # assign ammount of likes to post.likes_count variable
        like_btn = "Like"  # Default value of like/not like button
        if current_user.is_authenticated: 
            # Check if signed user likes this post
            try:
                like = Likes.objects.get(post=post, user=current_user)
                like_btn = "Unlike" # If he likes.. then he can "Unlike" the post
            except Likes.DoesNotExist:
                pass # If he doesn't like then button stays on "Like"

        post.like_btn = like_btn    # assign the value of button like/unlike

    # Pagination settings
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return posts_list,page_obj

# form for new posts
class CreateNewPostForm(forms.Form):
    post = forms.CharField(max_length=128,widget=forms.Textarea(attrs={'placeholder': 'How are you? :)'}))

# index view, displays all of the posts and form for creating new ones
def index(request):
    current_user = request.user
    if request.method == 'POST':
        form = CreateNewPostForm(request.POST) # assign forms values to form variable 
        if form.is_valid():
            post = form.cleaned_data['post'] 
            user = User.objects.get(username=current_user) 
            new_post = Post(user=user, post=post)
            new_post.save()
            return HttpResponseRedirect(reverse("index"))

    posts_list, page_obj = pagination(request, current_user,Post.objects.all().order_by('-timestamp'))
    return render(request, "network/index.html",{
        'form': CreateNewPostForm(),
        'posts_list':posts_list,
        'page_obj': page_obj,
        })

def profile_view(request, user_id):
    current_user = request.user
    follow = '' # Value fo follow button
    creator = User.objects.get(id=user_id) # Creator of post
    
    if current_user.is_authenticated:
        current_user_obj = User.objects.get(id=current_user.id)
        if creator.followers.filter(id=current_user.id):
            # method for unfollow
            follow = 'Unfollow'
            if request.method == 'POST':
                creator.followers.remove(current_user_obj)
                return HttpResponseRedirect(reverse("profile_view", args=(user_id,)))
        else:
            # method for follow
            follow = 'Follow'
            if request.method == 'POST':
                creator.followers.add(current_user_obj)  
                return HttpResponseRedirect(reverse("profile_view", args=(user_id,)))

    posts_list, page_obj = pagination(request, current_user,Post.objects.filter(user=creator).order_by('-timestamp'))
    
    return render(request, 'network/profile.html',{
        'creator': creator,
        'creator_id': user_id,
        'follow': follow,
        'posts_list':posts_list,
        'page_obj': page_obj
    })

def following_view(request):
    current_user = request.user
    if current_user.is_authenticated:
        # Get users that the current user follows
        current_user = User.objects.get(id=current_user.id)
        user_following = current_user.following.all()
        
        posts_list, page_obj = pagination(request, current_user,Post.objects.filter(user__in=user_following).order_by('-timestamp'))
        
        return render(request, 'network/following.html', {
            'posts_list':posts_list,
            'page_obj': page_obj
        })
    return HttpResponseRedirect(reverse("index"))

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
def edit_post(request):
    if request.method != "POST": # Editing post must be via POST
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    post_data = data.get('post')
    post_id = data.get('id')
    
    post = Post.objects.get(id=post_id)  
    post.post = post_data
    post.save()

    return JsonResponse({"message": post_data}, status=201)


@csrf_exempt
def like_post(request):
    if request.method != "POST": # Liking post must be via POST
        return JsonResponse({"error": "POST request required."}, status=400)
    
    data = json.loads(request.body)
    post_id = data.get('post_id')
    user_id = data.get('user_id')
    
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, id=user_id)

    new_likes_count = Likes.objects.filter(post=post).count()
    # Check if the user has already liked the post
    if Likes.objects.filter(user=user, post=post).exists():
        Likes.objects.filter(user=user, post=post).delete()
        return JsonResponse({"success": True, "new_likes_count": new_likes_count-1, "like_btn_value": "Like"}, status=201)
    else:
        # Create a new like instance
        like = Likes(post=post, user=user)
        like.save()
        return JsonResponse({"success": True, "new_likes_count": new_likes_count+1, "like_btn_value": "Unlike"}, status=201)