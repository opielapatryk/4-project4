from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import Post, User, Likes
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404


class CreateNewPostForm(forms.Form):
    post = forms.CharField(max_length=128,widget=forms.Textarea(attrs={'placeholder': 'How are you? :)'}))

def index(request):
    if request.method == 'POST':
        form = CreateNewPostForm(request.POST)
        if form.is_valid():
            post = form.cleaned_data['post']
            user = User.objects.get(username=request.user)
            new_post = Post(user=user, post=post)
            new_post.save()
            return HttpResponseRedirect(reverse("index"))

    posts_list = Post.objects.all().order_by('-timestamp')

    for post in posts_list:
        post.likes_count = Likes.objects.filter(post=post).count()

        # Check if user likes this post
        like_btn = "Like"  # Default value
        if request.user.is_authenticated:
            try:
                like = Likes.objects.get(post=post, user=request.user)
                like_btn = "Unlike"
            except Likes.DoesNotExist:
                pass

        post.like_btn = like_btn

    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html",{
        'form': CreateNewPostForm(),
        'posts_list':posts_list,
        'page_obj': page_obj,
        })

def profile_view(request, user_id):
    follow = ''
    creator = User.objects.get(id=user_id)
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if request.method == 'POST':
            if creator.followers.filter(id=request.user.id):
                # method for unfollow
                creator.followers.remove(current_user)
            else:
                # method for follow
                creator.followers.add(current_user)  

            return HttpResponseRedirect(reverse("profile_view", args=(user_id,)))

    # if you dont follow
    if request.user.is_authenticated:
        if creator.followers.filter(id=request.user.id):
            follow = 'Unfollow'
        else:
            # If you follow
            follow = 'Follow'

    posts_list = Post.objects.filter(user=creator).order_by('-timestamp')
    for post in posts_list:
        post.likes_count = Likes.objects.filter(post=post).count()

        # Check if user likes this post
        like_btn = "Like"  # Default value
        if request.user.is_authenticated:
            try:
                like = Likes.objects.get(post=post, user=request.user)
                like_btn = "Unlike"
            except Likes.DoesNotExist:
                pass

        post.like_btn = like_btn
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'network/profile.html',{
        'creator': creator,
        'creator_id': user_id,
        'follow': follow,
        'posts_list':posts_list,
        'page_obj': page_obj
    })

def following_view(request):
    if request.user.is_authenticated:
        # Get users that the current user follows
        current_user = User.objects.get(id=request.user.id)
        user_following = current_user.following.all()
        
        # Get posts from users that the current user follows
        posts_list = Post.objects.filter(user__in=user_following).order_by('-timestamp')
        for post in posts_list:
            post.likes_count = Likes.objects.filter(post=post).count()

            # Check if user likes this post
            like_btn = "Like"  # Default value
            if request.user.is_authenticated:
                try:
                    like = Likes.objects.get(post=post, user=request.user)
                    like_btn = "Unlike"
                except Likes.DoesNotExist:
                    pass

            post.like_btn = like_btn
        paginator = Paginator(posts_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

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
    # Editing post must be via POST
    if request.method != "POST":
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
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
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
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
